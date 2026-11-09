"""Make an itsy.page with the Gemini API.

Google calls the itsy.page MCP server for you (remote MCP in the Interactions
API), so there is no MCP client to run.

    pip install "google-genai>=2.31,<3"
    export GEMINI_API_KEY=...
    python interactions.py "A page for my bake sale on Saturday at 10am in Moda Park"
"""

import sys

from google import genai

client = genai.Client()
request = " ".join(sys.argv[1:]) or "Make a fun page for my birthday picnic on July 20 at 4pm in Moda Park."

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=request,
    system_instruction=(
        "Publish the page the user describes on itsy.page with the itsy_page tools. "
        "Do not ask follow-up questions; make sensible choices and skip private details you were not given. "
        "Reply with the public link and the secret edit link, and say the edit link works like a password."
    ),
    # The server name must not contain "-".
    tools=[{"type": "mcp_server", "name": "itsy_page", "url": "https://api.itsy.page/mcp"}],
)

print(interaction.output_text)
