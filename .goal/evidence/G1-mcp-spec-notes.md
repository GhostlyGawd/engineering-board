# MCP spec grounding (fetched 2026-07-04, spec 2025-06-18)
- Protocol version string: "2025-06-18"
- stdio transport: JSON-RPC 2.0 over stdin/stdout (newline-delimited)
- Handshake: client->`initialize` {protocolVersion, capabilities, clientInfo} ->
  server responds {protocolVersion, capabilities:{tools:{listChanged}}, serverInfo, instructions?}
  -> client sends notification `notifications/initialized`
- `tools/list` -> {tools:[{name, description, inputSchema(JSON Schema), title?}]}
- `tools/call` {name, arguments} -> {content:[{type:"text", text}], isError?}
- Shutdown (stdio): client closes server's stdin, waits, SIGTERM/SIGKILL.
Source: https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle

# Claude Code plugin grounding (fetched 2026-07-04)
- plugin.json required: name; optional: description, version, author{name}, homepage, repository, license, keywords
- Component dirs at plugin ROOT (NOT inside .claude-plugin/): commands/ agents/ skills/ hooks/ .mcp.json .lsp.json
- A plugin can BUNDLE an MCP server via `.mcp.json` at plugin root -> dual distribution from one repo
- Validate: `claude plugin validate`
- Install: `/plugin marketplace add <owner/repo>` then `/plugin install <name>`
- Community submission: platform.claude.com/plugins/submit (Console) or claude.ai/admin-settings/directory/submissions/plugins/new
Source: https://code.claude.com/docs/en/plugins
