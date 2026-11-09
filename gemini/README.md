# itsy.page with Google Gemini

Every path below uses the same remote MCP server, `https://api.itsy.page/mcp` (Streamable HTTP, no authentication). Google moves and renames these screens often. The steps follow Google's documentation as of October 2026.

| Where | How | Voice |
|-------|-----|-------|
| Gemini app (gemini.google.com) | Custom app from the MCP URL | Typed or dictated prompts |
| Gemini Enterprise | Custom MCP data store, or an ADK agent | Typed |
| Gemini CLI | Extension (this folder's parent) | No |
| Antigravity | Plugin (this folder's parent) | No |
| Gemini API | Remote MCP in the Interactions API: [interactions.py](./interactions.py) | No |
| Gemini Live API | Voice app: [live/itsy_live.py](./live/itsy_live.py) | Yes, spoken conversation |
| Agent Development Kit | Agent: [adk/itsy_agent](./adk/itsy_agent) | Through your own front end |

## Gemini app

Custom apps connect an MCP server to Gemini by URL. Requirements at launch: a personal Google account (not work or school), age 18 or older, in the US, English, with Keep Activity on. Plan availability varies.

1. On the web, open gemini.google.com → Settings → **Connected apps**. If you don't see it, turn on Personal Intelligence first.
2. Under **Custom apps**, choose **Add a custom app**.
3. Paste `https://api.itsy.page/mcp` and continue. itsy.page needs no sign-in, so leave the advanced credential fields empty.
4. In any chat on the web or the mobile app, mention the app (for example `@itsy.page make a page for my bake sale`). Gemini asks you to confirm each publish, edit, or delete.

Google's help pages describe sign-in through dynamic client registration or manual credentials. They don't say whether a server without sign-in is accepted. Test this before announcing the integration.

## Gemini Enterprise

**Standard and Plus (Google Cloud console):** an admin with `roles/discoveryengine.editor` opens Gemini Enterprise → Data stores → Create data store → **Custom MCP Server**, adds `https://api.itsy.page/mcp` with **No authentication**, then opens Actions → **Reload custom actions** and enables the tools. If the organization restricts Custom MCP data stores or egress domains, allow `api.itsy.page` in those organization policies first. Tools marked read-only (`get_page_guide`, `check_page_name`, `get_page`) run without asking for confirmation. Gemini asks the user to confirm the others.

**Business (business.gemini.google):** Settings & help → Manage team → **Connected apps** → Add MCP Server, enter the URL and the name `itsy.page`, choose **No authentication**, add it, then enable it for the team.

**As an agent:** deploy [adk/itsy_agent](./adk/itsy_agent) to Agent Runtime (see below). Then Gemini Enterprise → Agents → Add agent → **Custom agent via Agent Runtime**, and enter its `projects/<project>/locations/<region>/reasoningEngines/<id>` name.

## Gemini CLI

The parent folder is a Gemini CLI extension (`gemini-extension.json` and `GEMINI.md`):

```bash
gemini extensions install https://github.com/keremozcan/itsypage-integrations
```

Without the extension, add the server to `~/.gemini/settings.json`. Use `httpUrl`, because `url` means SSE in Gemini CLI:

```json
{ "mcpServers": { "itsy-page": { "httpUrl": "https://api.itsy.page/mcp" } } }
```

The extension gallery at geminicli.com/extensions lists public repositories with the manifest at their root, the `gemini-cli-extension` topic and a release tag. `keremozcan/itsypage-integrations` is set up that way; the gallery crawls daily.

## Antigravity

The parent folder is also an Antigravity plugin (`plugin.json`, `mcp_config.json`, `skills/make-itsy-page`):

```bash
agy plugin install https://github.com/keremozcan/itsypage-integrations
```

Or copy the folder to `~/.gemini/config/plugins/itsy-page/`, or to `.agents/plugins/itsy-page/` for one workspace. Without the plugin, add the server to `~/.gemini/config/mcp_config.json`. Antigravity reads `serverUrl`, not `url` or `httpUrl`:

```json
{ "mcpServers": { "itsy-page": { "serverUrl": "https://api.itsy.page/mcp" } } }
```

The official Antigravity marketplace is curated. Request a listing through Google's plugin interest form, linked from antigravity.google/docs/marketplace.

## Gemini API

With remote MCP in the Interactions API, Google calls the server for you:

```bash
pip install "google-genai>=2.31,<3"
export GEMINI_API_KEY=...
python interactions.py "A page for my bake sale on Saturday at 10am in Moda Park"
```

The same request in JavaScript:

```js
import { GoogleGenAI } from '@google/genai'

const interaction = await new GoogleGenAI({}).interactions.create({
  model: 'gemini-3.8-flash',
  input: 'A page for my bake sale on Saturday at 10am in Moda Park',
  tools: [{ type: 'mcp_server', name: 'itsy_page', url: 'https://api.itsy.page/mcp' }],
})
console.log(interaction.output_text)
```

The server `name` must not contain `-`. The edit key comes back in the model's reply, so treat logs of these calls as secrets.

To run the MCP client yourself, pass a connected `mcp.ClientSession` in `tools` of `generate_content` (Python) or wrap the client with `mcpToTool` (JavaScript). The SDK then calls the tools automatically.

## Voice with Gemini Live

[live/itsy_live.py](./live/itsy_live.py) is a small voice app. You describe the page, Gemini asks for anything missing, and the page is published. The links are printed on screen, not read aloud.

```bash
cd live
pip install -r requirements.txt   # PyAudio needs PortAudio (brew install portaudio / apt install portaudio19-dev)
export GEMINI_API_KEY=...
python itsy_live.py               # talk
python itsy_live.py --text        # type; replies are still spoken
python -m unittest test_itsy_live.py
```

The Live API doesn't run MCP tools by itself. The app turns the server's tools into blocking function declarations and answers each tool call with the matching MCP call. Use headphones so Gemini doesn't hear itself. Set `ITSY_MCP_URL` to point at a local API (`http://localhost:3001/mcp`).

## Agent Development Kit

```bash
cd adk
pip install -r requirements.txt
export GOOGLE_API_KEY=...          # or Vertex AI credentials
adk web                            # chat with the agent in the browser
adk deploy agent_engine --project=<project> --region=us-central1 --display_name="itsy.page" itsy_agent
```

ADK shows the page card (an MCP Apps view) as a UI widget in hosts that render them.
