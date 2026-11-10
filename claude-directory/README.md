# Listing itsy.page in Claude's Connectors Directory

Anyone can already add `https://api.itsy.page/mcp` as a custom connector (see [../README.md](../README.md#claude-claudeai-desktop-mobile)). A directory listing lets people find it in Claude and add it with one click.

This page holds everything the developer portal asks for, step by step, so the form is copy and paste. It follows Anthropic's [submission guide](https://claude.com/docs/connectors/building/submission) and [review checklist](https://claude.com/docs/connectors/building/review-criteria) as read on 10 Nov 2026; check them again before submitting, because the form changes.

**Who submits:** Kerem, from a paid Claude account, at [claude.ai/directory/manage](https://claude.ai/directory/manage) → **Submit new** → **MCP connector**. Anthropic scans it automatically and lists it as a Community connector by default; some get a human review. Escalations: `mcp-review@anthropic.com`.

**One listing, itsy.page.** The server also serves minisayfa.com pages through the `brand` argument, and the directory wants the server domain to match the service, so minisayfa.com gets no listing of its own for now.

## Before opening the portal

1. **Test it in Claude** (the portal makes you confirm this). **Done 10 Nov 2026** on Kerem's claude.ai account (custom connector "itsy.page", no sign-in detected automatically, Opus 5.5): all six test prompts below passed. Claude called `create_page`, `update_page_settings`, `get_page` + `update_page`, `check_page_name`, `email_edit_link` (the email arrived in the inbox from no-reply@itsy.page) and `delete_page` (the page then redirected to the claim screen). The card rendered in Claude's dark theme with the page, the edit link and copy buttons. `get_page_guide` was not needed in that chat; it was run directly against the server along with every other tool. Re-run this if the server's tools change before submitting.
2. Have the icon ready: `frontend/public/favicon-512x512.png`.
3. Have the four carousel screenshots ready: [screenshots/](./screenshots/). Regenerate them with `node scripts/render-mcp-card-screenshots.mjs` after a change to `backend/mcpWidget.mjs`.

## Requirements check

| Requirement | Status |
|---|---|
| Remote, HTTPS | `https://api.itsy.page/mcp`, Streamable HTTP, stateless |
| Authentication | None. No user accounts exist; creating a page needs nothing, and changing one needs that page's secret edit key. OAuth is only required for tools that act on a user's account. |
| Every tool has `title` + `readOnlyHint`/`destructiveHint` | Yes, all 8 (`backend/mcpServer.mjs`, `TOOL_DEFINITIONS`) |
| Read and write split into separate tools | Yes: 3 read, 5 write; no catch-all request tool |
| Tool names ≤ 64 characters | Yes |
| No prompt-injection patterns in descriptions | The descriptions say what each tool does and when to call it; none points Claude at other tools or outside instructions |
| Own first-party API | Yes, the itsy.page API |
| No money transfer, no AI image/video/audio | Yes. No purchase links in tool results; a premium publish code the user already owns can be redeemed |
| No conversation data beyond the tool's needs | Only the tool arguments reach us, and we store only what makes up the page. Access logs record the path and status (edit tokens redacted), never the request body. |
| Privacy policy | https://itsy.page/privacy, with an "AI assistants" section on what the assistant's provider receives |
| Public documentation | https://itsy.page/developers and https://itsy.page/api.md#mcp-server-chatgpt-claude-and-other-assistants |
| MCP App carousel: 3–5 PNG, ≥ 1000px wide, cropped to the app | 4 PNGs, 1120px wide, card only |

**Weak spot to know about:** some error messages are terse. `get_page` on a missing name returns "Reading the page failed: NOT_FOUND. Not found". The review checklist fails generic errors with no detail. This one names the code, so it should pass, but a plainer message ("No itsy.page page is called kerem") would be safer.

## Portal steps

### 1. Connection

- URL: `https://api.itsy.page/mcp`
- Users connect to different URLs: **no**

### 2. Tools

These sync from the server. Expected: 8 tools, plus the `make_page` prompt and the `ui://widget/itsy-page.html` resource. Nothing should be flagged.

- Read-only: `get_page_guide`, `check_page_name`, `get_page`
- Write: `create_page`, `email_edit_link`
- Write, destructive: `update_page`, `update_page_settings`, `delete_page`

### 3. Listing

- **Server name** (≤ 100): `itsy.page`
- **One-liner** (≤ 200): `Make a tiny one-page website by chatting: party invites, link-in-bio pages, menus and event pages, published at once with a link to share. No account needed.`
- **Description** (≤ 2,000):

  > Tell Claude what the page is for and it builds and publishes a small website on itsy.page in one go, with a link you can share right away. It works for a birthday invite with a countdown and a map, a link-in-bio page, a café menu, a bake sale, a club announcement or a simple poll.
  >
  > There is no account and no sign-up. Every new page comes with a secret edit link that works like a password for that page. Keep it, and later you can ask Claude to change the text, add a poll, switch the colours, turn reactions off, rename the page or take it down. Claude can also email the edit link to you, which helps in voice conversations.
  >
  > What Claude can do:
  > • Check whether a page name is free
  > • Publish a new page from your description
  > • Read a page, and with its edit link, change its content or settings
  > • Email the secret edit link to an address you give
  > • Delete a page, only after you confirm
  >
  > Pages are public as soon as they are published. Anyone who has the edit link can change the page, so share it only with people you trust.

- **Categories** (1–5): Productivity; Design (pick the closest the portal offers)
- **Documentation URL:** `https://itsy.page/developers`
- **Privacy policy URL:** `https://itsy.page/privacy`
- **Support contact:** `hello@itsy.page`
- **Icon:** `frontend/public/favicon-512x512.png`
- **URL slug** (permanent): `itsy-page`

### 4. Use cases

- **Primary use cases:** publish a one-page website for an event, invitation, link-in-bio, menu or announcement; edit or delete a page made earlier; email yourself the edit link.
- **What users need before connecting:** nothing. No account, plan or setup.
- **Reads or writes data:** both.

### 5. Company

- **Company name:** itsy.page
- **Website:** `https://itsy.page`
- **Primary contact for review updates:** Kerem (his own email)

### 6. Authentication

- **Authentication requirement:** none (no sign-in)
- **Authentication methods:** none

### 7. Data handling

- **Underlying API:** our own (the itsy.page API; the MCP server is part of the same backend)
- **Personal health data:** no
- **Sponsored content:** no

### 8. Test & launch

Paste as the reviewer instructions:

> No account or credentials are needed. Add https://api.itsy.page/mcp as a custom connector with no authentication.
>
> 1. Ask: "Make a page for my birthday party on July 20 at 7pm at Moda Park. Make it fun." Claude calls create_page and gets back the public URL and a secret edit link (https://itsy.page/XXXX-XXXX-XXXX). The edit key inside that link is what every edit tool needs.
> 2. Ask: "Change the colour of my page to green and turn off reactions." → update_page_settings.
> 3. Ask: "Add a poll asking whether people want pizza or tacos." → get_page with the edit key, then update_page.
> 4. Ask: "Is the name crumbs-bakery free?" → check_page_name.
> 5. Ask: "Email my edit link to me at <your address>." → email_edit_link (sends one real email).
> 6. Ask: "Delete my page." → delete_page. With one page in the conversation, Claude takes the request as the confirmation and deletes it; if it is unclear which page is meant, it asks first.
>
> get_page_guide is called by Claude on its own when it needs the page syntax. Pages made during review can be deleted with step 6, or we remove them on request.

Then tick that every tool was run (step 1 of "Before opening the portal").

**Allowed link URIs (optional):** `https://itsy.page`. The card's "Open page" button opens `https://<name>.itsy.page/`. Subdomains can't be listed as a wildcard, so that click shows Claude's "Open external link" confirmation. That is fine.

**Carousel screenshots, with their paired prompts:**

| File | Prompt |
|---|---|
| `screenshots/1-birthday-published.png` | Make a page for my birthday party on July 20 at 7pm at Moda Park, with a countdown and a pizza-or-tacos poll. |
| `screenshots/2-bakery-link-in-bio.png` | Create a link-in-bio page for my bakery Crumbs with my Instagram, my menu and my email. |
| `screenshots/3-page-updated.png` | Add a second poll to my party page asking what time people can come. |
| `screenshots/4-menu-dark.png` | Make a one-page menu for Moda Kahve with coffees, teas and cakes, and a map to the café. |

### 9. Compliance

Seven acknowledgments: directory guidelines, first-party API use, financial transactions, AI media generation, prompt injection, conversation data collection, public documentation. All seven hold (see the requirements check above).

### 10. Review and submit

Read the quality warnings the portal shows, fix anything it flags, then submit. Note the date and the submission status in `docs/team/STATE.md`.
