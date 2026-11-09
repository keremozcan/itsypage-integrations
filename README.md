# itsy.page for AI assistants

Build and publish a tiny one-page website by talking or typing to an assistant. There is no account: the assistant gets back a public link and a secret edit link that works like a password for the page.

Everything here connects to one remote MCP server:

```text
https://api.itsy.page/mcp
```

It is a stateless Streamable HTTP server with no authentication. Its tools are `get_page_guide`, `check_page_name`, `create_page`, `get_page`, `update_page`, `update_page_settings`, `email_edit_link`, and `delete_page`. Page tools return a small card (an MCP Apps view) in hosts that render them. Full reference: [API docs — MCP Server](https://itsy.page/api.md#mcp-server-chatgpt-claude-and-other-assistants).

This folder is published as its own public repository, [keremozcan/itsypage-integrations](https://github.com/keremozcan/itsypage-integrations), so its manifests sit at the repository root where the install commands below look for them. It is copied there from the `integrations/` folder of the main itsy.page repository on every change, so edits made here directly are overwritten.

## ChatGPT

Add a custom MCP server: on chatgpt.com, open the plugins (apps) settings, choose **Add custom MCP server**, paste `https://api.itsy.page/mcp`, pick **No authentication**, and create it. ChatGPT renames these screens often, so the wording above may have moved. Custom GPTs can import `https://itsy.page/openapi.json` instead.

To list itsy.page in ChatGPT's directory, see [chatgpt/README.md](./chatgpt/README.md).

## Claude (claude.ai, Desktop, mobile)

Customize → Connectors → **Add custom connector**, paste `https://api.itsy.page/mcp`, and choose no sign-in. On Team and Enterprise plans an owner adds it under Organization settings → Connectors. Voice mode can use connectors, so you can make a page by talking.

## Claude Code

```bash
/plugin marketplace add keremozcan/itsypage-integrations
/plugin install itsy-page@itsypage
```

The plugin adds the MCP server and a `make-itsy-page` skill. Without the plugin:

```bash
claude mcp add --transport http itsy-page https://api.itsy.page/mcp
```

## Cursor

One-click install link:

```text
cursor://anysphere.cursor-deeplink/mcp/install?name=itsy-page&config=eyJ1cmwiOiJodHRwczovL2FwaS5pdHN5LnBhZ2UvbWNwIn0=
```

Or add to `~/.cursor/mcp.json`:

```json
{ "mcpServers": { "itsy-page": { "url": "https://api.itsy.page/mcp" } } }
```

## VS Code (GitHub Copilot)

One-click install link:

```text
vscode:mcp/install?%7B%22name%22%3A%22itsy-page%22%2C%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fapi.itsy.page%2Fmcp%22%7D
```

Or run `code --add-mcp '{"name":"itsy-page","type":"http","url":"https://api.itsy.page/mcp"}'`.

## Google Gemini

- **Gemini app:** on the web, Settings → Connected apps → **Add a custom app**, paste `https://api.itsy.page/mcp`, then mention the app in any chat.
- **Gemini Enterprise:** an admin adds a Custom MCP Server data store (Business edition: Connected apps → Add MCP Server) with no authentication, or registers the ADK agent.
- **Gemini CLI and Antigravity:** this folder is both a Gemini CLI extension (`gemini-extension.json`, `GEMINI.md`) and an Antigravity plugin (`plugin.json`, `mcp_config.json`, `skills/`):

  ```bash
  gemini extensions install https://github.com/keremozcan/itsypage-integrations
  agy plugin install https://github.com/keremozcan/itsypage-integrations
  ```

- **Gemini API, Live voice, and ADK:** samples in [gemini/](./gemini/README.md), including a voice app where you talk to Gemini and it publishes the page.

Manual config uses a different key in each client: Gemini CLI `httpUrl` in `~/.gemini/settings.json`, Antigravity `serverUrl` in `~/.gemini/config/mcp_config.json`. Step-by-step setup for every Gemini surface: [gemini/README.md](./gemini/README.md).

## Other MCP clients

Add a remote Streamable HTTP server named `itsy-page` with the URL above and no authentication.

## Discovery

- Server card: `https://api.itsy.page/mcp/server-card` (MCP Server Card extension)
- AI catalog: `https://itsy.page/.well-known/ai-catalog.json`
- MCP Registry entry: [mcp-registry/server.json](./mcp-registry/server.json); publishing steps in [mcp-registry/README.md](./mcp-registry/README.md)

## What assistants can and cannot do

They can publish pages with text, buttons, GIFs, polls, random pickers, countdowns, contact icons, profiles, embeds (YouTube, Spotify, Google Maps, payment links, …), themes, and reactions; change content and settings later in the same conversation; rename; email the edit link; and delete after confirmation. They cannot upload photos or files from the chat; add those in the browser editor with the edit link. Premium names and features follow the same rules as the website.
