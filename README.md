# mc-iclone8-mcp

[Français](README.fr.md)

A local MCP server for controlling iClone 8 through its official Python API.

The iClone plugin provides a small start/stop window. The MCP endpoint is local
only and defaults to `http://127.0.0.1:8766/mcp`. All iClone commands are sent
back to iClone's main thread before they run.

## Requirements

- iClone 8 on Windows.
- A client supporting Streamable HTTP MCP, such as Codex.

## Install the iClone plugin

1. Copy this repository folder to:

   ```text
   <iClone 8>\Bin64\OpenPlugin\mc-iclone8-mcp
   ```

2. Start iClone 8 and load the plugin.
3. Open **Plugins → mc-iclone8-mcp → Open MCP server**.
4. Select **Start**. The status must show `http://127.0.0.1:8766/mcp`.

The server deliberately binds to `127.0.0.1`: it is intended for the computer
running iClone, not for a network connection.

## Install as a Codex MCP server

Keep iClone open and start the server first. Then run:

```powershell
codex mcp add mc-iclone8-mcp --url http://127.0.0.1:8766/mcp
```

Restart Codex (or start a new task) after adding it. Confirm the configuration
with:

```powershell
codex mcp list
```

Alternatively, add the following to `%USERPROFILE%\.codex\config.toml` (or to
the project’s `.codex\config.toml`):

```toml
[mcp_servers.mc-iclone8-mcp]
url = "http://127.0.0.1:8766/mcp"
startup_timeout_sec = 15
tool_timeout_sec = 60
```

An identical ready-to-copy sample is available at
[`examples/codex-config.toml`](examples/codex-config.toml).

## Available capabilities

The server exposes MCP tools to:

- inspect, select, transform, show, and remove scene objects;
- create official iClone primitives, import assets, and save projects;
- control the timeline, cameras, and lights;
- inspect and change materials and colors;
- inspect skin bones, animation clips, and morphs;
- load motions and export a single object as FBX.

The plugin targets iClone 8. It intentionally avoids iClone 7-only APIs,
including the motion-bone APIs removed in iClone 8.

## Development

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
```

The main technical reference is the official [iClone 8 Python API
documentation](https://wiki.reallusion.com/IC8_Python_API).
