# Listing itsy.page in ChatGPT

> **30 Oct 2026: the ChatGPT route is now a plugin built on the MCP server.** OpenAI renamed ChatGPT apps to plugins (9 Jul 2026). Custom GPTs retire on 11 Dec 2026 and their Actions do not migrate, so itsy.page builds no Custom GPT or GPT Action; ChatGPT users reach it through the plugin. The package is [plugin/](./plugin/): `.codex-plugin/plugin.json` (identity and listing texts, no secrets), `.mcp.json` (the one MCP server, `https://api.itsy.page/mcp`, no authentication) and `assets/logo.png`. Zip the contents of `plugin/` and upload it at platform.openai.com/plugins → "Upload new or existing plugin" → "With MCP". Keep `version` in step with `MCP_SERVER_VERSION`. The ZIP must contain no secrets, hooks or app references.

Anyone can already add `https://api.itsy.page/mcp` as a custom MCP server (see [../README.md](../README.md#chatgpt)). A directory listing lets people add it with one click. Submission happens on platform.openai.com (plugins), needs a verified individual or business, and is reviewed by OpenAI. The steps below follow OpenAI's Apps SDK submission docs as of October 2026; check them again before submitting, because the form changes.

## Before submitting

1. Deploy the API with the MCP server and confirm `https://api.itsy.page/mcp` answers `initialize` and `tools/list`.
2. Domain verification: OpenAI gives you a token to serve at `https://api.itsy.page/.well-known/openai-apps-challenge`. The API serves it from the `OPENAI_APPS_CHALLENGE` environment variable (plain text; 404 while unset), so set the variable on the API host and restart; the token never goes in this repo.
3. Have a demo video of a spoken or typed conversation that publishes a page.

## Listing metadata

| Field | Value |
|-------|-------|
| Display name (max 30) | itsy.page |
| Short description (max 30) | Make a tiny website by chatting |
| Long description | Describe the page you want, such as a birthday invite, a bake sale, a link-in-bio, or a menu, and ChatGPT publishes it on itsy.page with a shareable link. No account: you get a secret edit link for later changes. |
| Developer | itsy.page |
| Category | Productivity |
| Logo | `frontend/public/favicon-512x512.png` |
| Website | https://itsy.page |
| Support | https://itsy.page/contact |
| Privacy policy | https://itsy.page/privacy |
| Terms | https://itsy.page/terms |
| MCP server | https://api.itsy.page/mcp (no authentication) |

Every tool has a `title` plus `readOnlyHint`, `destructiveHint`, and `openWorldHint` annotations. `delete_page`, `update_page` (replacing blocks drops removed blocks' poll votes and counts) and `update_page_settings` (a rename leaves the old URL without a redirect) are marked destructive; the three are idempotent. Tool results carry no Premium purchase or claim links (the plugin rules bar upsells for digital goods); a premium publish code the user already has still works through `premiumPublishCode`.

## Test cases

Positive (should publish or act):

1. "Make a page for my birthday party on July 20 at 7pm at Moda Park. Make it fun." → `create_page` with a party theme, a countdown, and reactions; returns the link and the secret edit link.
2. "Create a simple link-in-bio page for my bakery Crumbs with my Instagram @crumbsbakery and email hello@crumbs.example." → contact block with Instagram and email.
3. "Change the color of my page to green and turn off reactions." (after 1) → `update_page_settings`.
4. "Add a poll asking whether people want pizza or tacos." (after 1) → `get_page` with the edit key, then `update_page` keeping existing block ids.
5. "Email my edit link to me at ada@example.com." (after 1) → `email_edit_link`.

Negative (should not publish, or should stop):

1. "What is itsy.page?" → answer without calling write tools.
2. "Make a page that looks like the PayPal login page." → refuse (phishing/impersonation).
3. "Delete my page." without the user confirming which page → ask for confirmation and the edit link; do not call `delete_page` yet.
