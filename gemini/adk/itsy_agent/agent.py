"""An ADK agent that builds itsy.page pages.

Run locally with `adk web` from the parent folder, or deploy it to Agent
Runtime and register it in Gemini Enterprise (see ../../README.md).
"""

import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

MCP_URL = os.environ.get("ITSY_MCP_URL", "https://api.itsy.page/mcp")

# Defined synchronously at module level, as Agent Runtime deployment requires.
root_agent = LlmAgent(
    model="gemini-3.8-flash",
    name="itsy_page",
    description="Builds and publishes tiny one-page websites on itsy.page.",
    instruction=(
        "You help people make a tiny one-page website on itsy.page. "
        "Ask only for details that are missing, and ask before publishing private details such as a home address or phone number. "
        "Unless the user wants something serious, make it playful with a theme, reactions, a GIF, a poll, or a countdown. "
        "Call get_page_guide if you are unsure of the page script syntax, then create_page once. "
        "Share the public link. Give the secret edit link once and say it works like a password and cannot be recovered. "
        "For later changes use update_page_settings for looks, and get_page then update_page for content. "
        "Only call delete_page after the user clearly confirms."
    ),
    tools=[McpToolset(connection_params=StreamableHTTPConnectionParams(url=MCP_URL))],
)
