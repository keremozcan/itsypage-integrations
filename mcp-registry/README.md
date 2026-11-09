# Publishing to the MCP Registry

[server.json](./server.json) lists the remote server as `page.itsy/mcp` in the official MCP Registry (registry.modelcontextprotocol.io, still in preview). The `page.itsy/*` namespace requires proving control of `itsy.page`.

1. Install the publisher: `brew install mcp-publisher` (or a release binary from the registry repository).
2. Create a key: `openssl genpkey -algorithm Ed25519 -out key.pem`. Keep it out of the repository.
3. Prove the domain with one of:
   - DNS: a TXT record on `itsy.page` with `v=MCPv1; k=ed25519; p=<base64 public key>`, then `mcp-publisher login dns --domain itsy.page --private-key <hex private key>`.
   - HTTP (recommended, no DNS change): the name `page.itsy/mcp` is proven on `itsy.page`, which is the static front end, so the proof is a file in a front-end deploy. At publish time, add `frontend/public/.well-known/mcp-registry-auth` containing one line, `v=MCPv1; k=ed25519; p=<base64 public key>`, with Kerem's public key; deploy the front end and check `curl https://itsy.page/.well-known/mcp-registry-auth`; then `mcp-publisher login http --domain itsy.page --private-key <hex private key>`. The file holds only the public key, but it is added for the publish, never committed as a placeholder. (The API also serves the same path on `api.itsy.page` from the `MCP_REGISTRY_AUTH` variable, which proves only that host, not `page.itsy/*`.)
4. From this folder: `mcp-publisher publish`.
5. Check: `curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=page.itsy/mcp"`.

Bump `version` here, in `../plugins/itsy-page/.claude-plugin/plugin.json`, in `../chatgpt/plugin/.codex-plugin/plugin.json`, in `../gemini-extension.json`, and `MCP_SERVER_VERSION` in `backend/mcpServer.mjs` together. Registry versions are immutable: each publish needs a new one. `description` stays at 100 characters or fewer.
