"""Offline checks for the Live tool bridge: python -m unittest test_itsy_live.py"""

import asyncio
import unittest
from types import SimpleNamespace

from google.genai import types

import itsy_live


def text_result(text, structured=None, is_error=False):
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        structured_content=structured,
        is_error=is_error,
    )


class FakeMcp:
    def __init__(self, results):
        self.results = results
        self.calls = []

    async def call_tool(self, name, args):
        self.calls.append((name, args))
        result = self.results[name]
        if isinstance(result, Exception):
            raise result
        return result


def tool_call(*calls):
    return types.LiveServerToolCall(function_calls=[
        types.FunctionCall(id=f"call-{index}", name=name, args=args) for index, (name, args) in enumerate(calls)
    ])


class AnswerToolCallTest(unittest.TestCase):
    def test_answers_every_call_in_order_and_shows_published_links(self):
        page = {"publicUrl": "https://ada.itsy.page/", "editLink": "https://itsy.page/edit?siteName=ada#editKey=x"}
        mcp = FakeMcp({
            "check_page_name": text_result("ada is available."),
            "create_page": text_result("Published ada", page),
        })
        shown = []
        responses = asyncio.run(itsy_live.answer_tool_call(
            mcp, tool_call(("check_page_name", {"siteName": "ada"}), ("create_page", {"script": "name: ada"})), shown.append,
        ))
        self.assertEqual(mcp.calls, [("check_page_name", {"siteName": "ada"}), ("create_page", {"script": "name: ada"})])
        self.assertEqual([(r.id, r.name, r.response) for r in responses], [
            ("call-0", "check_page_name", {"output": "ada is available."}),
            ("call-1", "create_page", {"output": "Published ada"}),
        ])
        self.assertEqual(shown, [page])

    def test_reports_tool_errors_and_network_failures_without_raising(self):
        mcp = FakeMcp({
            "create_page": text_result("Name taken", {"publicUrl": "https://ada.itsy.page/"}, is_error=True),
            "get_page": ConnectionError("down"),
        })
        shown = []
        responses = asyncio.run(itsy_live.answer_tool_call(
            mcp, tool_call(("create_page", {}), ("get_page", {})), shown.append,
        ))
        self.assertEqual(responses[0].response, {"error": "Name taken"})
        self.assertIn("could not be reached (ConnectionError)", responses[1].response["error"])
        self.assertEqual(shown, [])


class FunctionDeclarationsTest(unittest.TestCase):
    def test_converts_mcp_schemas_and_blocks_until_tools_finish(self):
        tool = SimpleNamespace(name="create_page", title="Create", description="Publish a page", input_schema={
            "type": "object",
            "properties": {
                "script": {"type": "string", "examples": ["name: ada"]},
                "blocks": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
            },
            "required": ["script"],
            "additionalProperties": False,
        })
        [declaration] = itsy_live.function_declarations([tool])
        self.assertEqual(declaration.name, "create_page")
        self.assertEqual(declaration.behavior, types.Behavior.BLOCKING)
        self.assertEqual(declaration.parameters.required, ["script"])
        self.assertEqual(declaration.parameters.properties["script"].type, types.Type.STRING)


if __name__ == "__main__":
    unittest.main()
