# Configure agents with mc-iclone8-mcp

Start the server in iClone 8 before connecting an agent:

```text
http://127.0.0.1:8766/mcp
```

The server is local and uses MCP Streamable HTTP. Do not configure this
installation as `stdio`, `sse`, or a remote URL.

## Codex

```powershell
codex mcp add mc-iclone8-mcp --url http://127.0.0.1:8766/mcp
codex mcp list
```

Equivalent `%USERPROFILE%\.codex\config.toml` entry:

```toml
[mcp_servers.mc-iclone8-mcp]
url = "http://127.0.0.1:8766/mcp"
startup_timeout_sec = 15
tool_timeout_sec = 60
```

## Claude Code

```powershell
claude mcp add --transport http mc-iclone8-mcp http://127.0.0.1:8766/mcp --scope user
claude mcp list
```

For a shared project, replace `--scope user` with `--scope project`. Claude
Code will ask for approval before using a project-scoped server for the first
time.

## Pi coding agent

Pi uses an MCP configuration file through its MCP extension or package. In the
Pi agent `mcp.json`, use this HTTP entry:

```json
{
  "mcpServers": {
    "mc-iclone8-mcp": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:8766/mcp"
    }
  }
}
```

Install `pi-codemcp` if the Pi distribution in use does not already provide an
MCP client. Confirm that the server appears in Pi’s tool list.

## OpenClaw

OpenClaw versions and extensions may expose MCP differently. When the MCP HTTP
client is available, use this equivalent entry:

```json
{
  "mcpServers": {
    "mc-iclone8-mcp": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:8766/mcp"
    }
  }
}
```

Check the exact syntax for the installed version with `openclaw mcp --help`.
`openclaw mcp serve` primarily exposes OpenClaw as an MCP server/bridge; it is
not necessarily the MCP client needed to call iClone.

## VS Code

Create `.vscode/mcp.json` in the workspace:

```json
{
  "servers": {
    "mc-iclone8-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8766/mcp"
    }
  }
}
```

Use **MCP: List Servers** or **MCP: Start Server** in VS Code and confirm that
the tools are visible in Copilot/Agent mode.

## Hermes and other MCP clients

If the client supports Streamable HTTP, use this equivalent entry:

```json
{
  "name": "mc-iclone8-mcp",
  "type": "streamable-http",
  "url": "http://127.0.0.1:8766/mcp"
}
```

The enclosing key may be `mcpServers`, `servers`, or a GUI field depending on
the agent. If Hermes only supports `stdio`, it cannot call this HTTP server
directly without an MCP adapter.

## Install the expert skill

The [`skills/iclone8-mcp`](../skills/iclone8-mcp) folder contains the
`SKILL.md` skill for agents supporting the Agent Skills format. Copy the folder
to the agent’s skills directory:

```text
Codex       : %USERPROFILE%\.codex\skills\iclone8-mcp
Claude Code : .claude\skills\iclone8-mcp
Project     : .agents\skills\iclone8-mcp
```

The skill formalizes discovery, tool selection, destructive-operation
confirmations, result verification, and prompt structure for scenes,
animations, cameras, materials, avatars, and rendering.

## Common smoke test

After starting the iClone server, ask the agent:

> Use mc-iclone8-mcp. Check the connection, list the available tools, and list
> the scene objects without changing anything.

The agent should start with `ping_iclone` or `get_api_version` and must not
create, delete, or animate anything for this test.
