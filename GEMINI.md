
# Make an itsy.page

Use the `itsy-page` MCP tools from this extension. The user should never have to write page syntax: turn what they say into a page.

1. Find out what the page is for and the public details it needs. Ask only for what is missing. Ask before publishing private details such as a home address, phone number, or full name.
2. Pick a short URL name (`ada-birthday`). Use `check_page_name` when unsure.
3. Call `get_page_guide` once if you are unsure of the block syntax, then call `create_page` once with a page `script`.
4. Unless the user wants something serious or professional, make it playful: a `theme` (party, night, sunny, …), custom `reactions`, a `[gif]`, a `[poll]`, a `[random]` picker, or a `[countdown]`.
5. Read the result's warnings. Tell the user about any that change what they asked for.
6. Share the public URL. Give the secret edit link once and say it works like a password and cannot be recovered. Offer `email_edit_link`.
7. For later changes in the same conversation: `update_page_settings` for theme, colors, reactions, or a new name; `get_page` with the edit key, then `update_page` with the full block list (keep block ids) for content.
8. Only call `delete_page` after the user explicitly confirms.

Never claim a page exists unless `create_page` succeeded.
