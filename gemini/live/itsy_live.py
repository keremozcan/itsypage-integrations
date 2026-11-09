"""Talk to Gemini and get an itsy.page.

A small voice app on the Gemini Live API. You describe the page out loud (or
type it with --text), Gemini asks for anything missing, and the itsy.page MCP
server publishes it. The public link and the secret edit link are printed on
your screen rather than read aloud.

    pip install -r requirements.txt
    export GEMINI_API_KEY=...
    python itsy_live.py            # speak (needs a microphone and speakers)
    python itsy_live.py --text     # type instead; replies are still spoken

The Live API does not run MCP tools by itself, so this file bridges them: it
turns the server's tools into function declarations and answers each tool call
with the result of the matching MCP call.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Any, Callable

from google import genai
from google.genai import types
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

MCP_URL = os.environ.get("ITSY_MCP_URL", "https://api.itsy.page/mcp")
MODEL = os.environ.get("ITSY_LIVE_MODEL", "gemini-3.8-live")

SEND_RATE = 16_000  # Live API input: 16-bit PCM, mono, 16 kHz
RECEIVE_RATE = 24_000  # Live API output: 16-bit PCM, mono, 24 kHz
CHUNK_FRAMES = 1024

SYSTEM_INSTRUCTION = """You help people make a tiny one-page website on itsy.page by talking.
Keep replies short and friendly; you are speaking, not writing.
Ask only for details that are missing, one question at a time. Ask before publishing private details such as a home address, phone number, or full name.
Unless the user wants something serious, make it playful: a theme, reactions, a GIF, a poll, or a countdown.
Call get_page_guide once if you are unsure of the page script syntax, then create_page once.
Never read a URL, edit key, or edit link aloud. Say the links are on the screen, and that the edit link works like a password and cannot be recovered.
For changes later in the conversation, use update_page_settings for looks and get_page then update_page for content.
Only call delete_page after the user clearly confirms."""

# JSON Schema keywords the SDK's schema model accepts; anything else (for
# example `examples`) is dropped before conversion.
_SCHEMA_KEYS = {field.alias or name for name, field in types.JSONSchema.model_fields.items()}
_SUBSCHEMA_KEYS = {"items", "additionalProperties"}
_SUBSCHEMA_LIST_KEYS = {"anyOf", "oneOf"}
_SUBSCHEMA_MAP_KEYS = {"properties", "$defs"}


def _supported_schema(schema: dict) -> dict:
    result = {}
    for key, value in schema.items():
        if key not in _SCHEMA_KEYS:
            continue
        if key in _SUBSCHEMA_KEYS:
            # The SDK converts only object subschemas, not `true`/`false`.
            if isinstance(value, dict):
                result[key] = _supported_schema(value)
        elif key in _SUBSCHEMA_LIST_KEYS:
            result[key] = [_supported_schema(item) for item in value]
        elif key in _SUBSCHEMA_MAP_KEYS:
            result[key] = {name: _supported_schema(sub) for name, sub in value.items()}
        else:
            result[key] = value
    return result


def function_declarations(mcp_tools: list[Any]) -> list[types.FunctionDeclaration]:
    """MCP tools as Live function declarations.

    BLOCKING makes Gemini wait for a publish to finish instead of talking over
    it or announcing a page that does not exist yet.
    """
    declarations = []
    for tool in mcp_tools:
        schema = _supported_schema(tool.input_schema or {"type": "object"})
        declarations.append(types.FunctionDeclaration(
            name=tool.name,
            description=tool.description or tool.title or tool.name,
            parameters=types.Schema.from_json_schema(json_schema=types.JSONSchema(**schema)),
            behavior=types.Behavior.BLOCKING,
        ))
    return declarations


def _result_text(result: Any) -> str:
    return "\n".join(block.text for block in result.content if getattr(block, "type", None) == "text")


def show_links(page: dict) -> None:
    """Default page callback: print the links for the person at the screen."""
    print(f"\n  Page:      {page['publicUrl']}", flush=True)
    if page.get("editLink"):
        print(f"  Edit link: {page['editLink']}", flush=True)
        print("  Keep the edit link private. Anyone with it can edit the page, and it cannot be recovered.\n", flush=True)


async def answer_tool_call(
    mcp: ClientSession,
    tool_call: types.LiveServerToolCall,
    on_page: Callable[[dict], None] = show_links,
) -> list[types.FunctionResponse]:
    """Run each requested MCP tool and build the Live function responses."""
    responses = []
    for call in tool_call.function_calls or []:
        try:
            result = await mcp.call_tool(call.name, call.args or {})
        except Exception as error:  # A network failure must not end the conversation.
            responses.append(types.FunctionResponse(
                id=call.id, name=call.name,
                response={"error": f"itsy.page could not be reached ({type(error).__name__}). Try again in a moment."},
            ))
            continue
        page = result.structured_content or {}
        if not result.is_error and page.get("publicUrl"):
            on_page(page)
        key = "error" if result.is_error else "output"
        responses.append(types.FunctionResponse(id=call.id, name=call.name, response={key: _result_text(result)}))
    return responses


async def receive_loop(session: Any, mcp: ClientSession, speaker: Any = None) -> None:
    """Play audio, show transcripts, and answer tool calls until the session ends."""
    while True:
        async for message in session.receive():
            if message.tool_call:
                await session.send_tool_response(function_responses=await answer_tool_call(mcp, message.tool_call))
                continue
            content = message.server_content
            if not content:
                continue
            if content.input_transcription and content.input_transcription.text:
                print(f"you: {content.input_transcription.text}", flush=True)
            if content.output_transcription and content.output_transcription.text:
                print(content.output_transcription.text, end="", flush=True)
            if speaker and content.model_turn:
                for part in content.model_turn.parts or []:
                    if part.inline_data and part.inline_data.data:
                        await asyncio.to_thread(speaker.write, part.inline_data.data)
            if content.turn_complete:
                print(flush=True)


async def send_microphone(session: Any, audio: Any) -> None:
    import pyaudio

    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=SEND_RATE, input=True, frames_per_buffer=CHUNK_FRAMES)
    print("Listening. Describe the page you want. Ctrl+C to stop.", flush=True)
    try:
        while True:
            data = await asyncio.to_thread(stream.read, CHUNK_FRAMES, exception_on_overflow=False)
            await session.send_realtime_input(audio=types.Blob(data=data, mime_type=f"audio/pcm;rate={SEND_RATE}"))
    finally:
        stream.close()


async def send_typed_text(session: Any) -> None:
    print("Type what you want, then Enter. Ctrl+D to stop.", flush=True)
    while True:
        line = await asyncio.to_thread(sys.stdin.readline)
        if not line:
            return
        if line.strip():
            await session.send_realtime_input(text=line.strip())


async def main(text_mode: bool) -> None:
    client = genai.Client()
    audio = speaker = None
    try:
        import pyaudio

        audio = pyaudio.PyAudio()
        speaker = audio.open(format=pyaudio.paInt16, channels=1, rate=RECEIVE_RATE, output=True)
    except Exception:
        if not text_mode:
            raise SystemExit("Voice mode needs PyAudio and a microphone. Install it, or run with --text.")
        print("(No audio output; showing transcripts only.)", flush=True)

    try:
        async with streamable_http_client(MCP_URL) as (read, write, *_):
            async with ClientSession(read, write) as mcp:
                await mcp.initialize()
                tools = (await mcp.list_tools()).tools
                config = types.LiveConnectConfig(
                    response_modalities=[types.Modality.AUDIO],
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=[types.Tool(function_declarations=function_declarations(tools))],
                    input_audio_transcription=types.AudioTranscriptionConfig(),
                    output_audio_transcription=types.AudioTranscriptionConfig(),
                )
                async with client.aio.live.connect(model=MODEL, config=config) as session:
                    sender = send_typed_text(session) if text_mode else send_microphone(session, audio)
                    receiver = asyncio.create_task(receive_loop(session, mcp, speaker))
                    try:
                        await sender
                    finally:
                        receiver.cancel()
    finally:
        if speaker:
            speaker.close()
        if audio:
            audio.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make an itsy.page by talking to Gemini.")
    parser.add_argument("--text", action="store_true", help="type instead of speaking")
    try:
        asyncio.run(main(parser.parse_args().text))
    except KeyboardInterrupt:
        pass
