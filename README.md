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

Configuration examples for Claude Code, Pi coding agent, OpenClaw, Hermes, and
VS Code are collected in [`docs/agent-configs.en.md`](docs/agent-configs.en.md).
The reusable expert skill is available in
[`skills/iclone8-mcp`](skills/iclone8-mcp).

## Available capabilities

Version `v0.1.0` exposes 60 MCP tools:

| Category | Tools | What they do |
| --- | --- | --- |
| Diagnostics | `ping_iclone`, `get_api_version`, `get_runtime_diagnostics` | Check connectivity, the targeted version, and available RLPy capabilities. |
| Scene and objects | `list_objects`, `get_selection`, `select_object`, `set_visibility`, `delete_object`, `clone_object`, `link_object`, `unlink_object`, `align_object`, `set_static` | Inspect, select, show/hide, delete, clone, link, unlink, and align objects. |
| Projects and assets | `create_primitive`, `save_project`, `get_project_info`, `import_asset`, `load_motion`, `preload_motion`, `load_substance_painter_textures`, `export_fbx` | Create primitives, import files, load motions, apply textures, save projects, and export FBX. |
| Transforms | `get_transform`, `set_transform`, `delete_transform_key`, `move_transform_key`, `set_transform_key_transition`, `clear_transform_keys` | Read and edit object position, rotation, scale, and animation keys. |
| Timeline | `get_timeline`, `set_timeline`, `play_timeline`, `pause_timeline`, `stop_timeline`, `clear_scene_animations` | Control playback, the playhead, and scene-animation removal. |
| Cameras | `get_camera`, `get_camera_capabilities`, `set_camera`, `set_camera_transform`, `set_camera_focal_key`, `set_camera_dof`, `set_current_camera`, `set_camera_look_at` | Inspect and animate cameras, set focal length, clipping, depth of field, the active camera, and object tracking. |
| Materials | `get_materials`, `set_material_color`, `set_material_texture`, `set_material_value` | Inspect materials, apply colors and textures, and animate opacity, glossiness, or self-illumination. |
| Lights | `get_light`, `set_light` | Inspect and change light activation, color, and intensity. |
| Avatars | `get_avatar_info`, `get_avatar_capabilities`, `get_skin_bones`, `get_animation_clips`, `set_clip_speed`, `set_clip_loop_count` | Inspect avatars, bones, components, and clips, then set clip speed and looping. |
| Morphs | `list_morphs`, `get_morph_weight`, `set_morph_weight` | List, read, and animate morph weights on compatible props and avatars. |
| Rendering | `get_render_settings`, `render_video` | Read the output resolution and start video rendering after explicit confirmation. |
| Mocap and networking | `get_mocap_status`, `get_network_capabilities` | Diagnose the mocap manager and native TCP/UDP availability. |

These tools can be used to:

- inspect, select, transform, show, and remove scene objects;
- create official iClone primitives, import assets, and save projects;
- control the timeline, cameras, and lights;
- inspect and change materials, colors, texture maps, opacity, glossiness, and self-illumination;
- inspect avatar components, skin bones, animation clips, loop counts, and morphs;
- load or pre-load motions, apply Substance Painter texture folders, and export a single object as FBX;
- inspect the current render size and start a render only after explicit confirmation;
- inspect iClone mocap state and native TCP/UDP availability without opening external connections.

The plugin targets iClone 8 exclusively through its official Python API.

## Example instructions for an agent

Give the agent a clear objective, object names, and numeric values. The agent
can inspect the scene first and then call the appropriate MCP tools.

| Category | Example instruction |
| --- | --- |
| Scene | “List the props in the scene, then select `MCP8_Live_Test_Box`.” |
| Creation | “Create a red box named `Logo_Block` at X=0, Y=0, Z=20, and add a floor beneath it.” |
| Transform | “Move `Logo_Block` to X=200 at frame 120 and scale it to 150%.” |
| Materials | “List the materials on `Logo_Block`, then set material 0 to royal blue and hide its diffuse texture.” |
| Texture maps | “Apply `C:\\Assets\\logo_basecolor.png` as the diffuse texture of material 0 on `Logo_Block`.” |
| Material animation | “At frame 300, set `Logo_Block` material 0 opacity to 0.25 and self-illumination to 0.8.” |
| Timeline | “Set the playhead to frame 0, play frames 0 through 300, then stop.” |
| Camera | “Read the active camera's focal length and set it to 50 mm.” |
| Animation | “Animate `Orbit_Sphere` around `Center_Cube` using transform keys at frames 0, 150, 300, 450, and 600.” |
| Avatar | “List the skin bones and animation clips on avatar `Character1`.” |
| Avatar playback | “Inspect `Character1` capabilities, then set clip 0 to loop three times at 1.2× speed.” |
| Morphs | “List the morphs on `Character1`, then set the specified facial morph to weight 0.5 at the current frame.” |
| Import/export | “Import this `.iProp` file, save the project, then export the selected object as FBX.” |
| Render | “Read the render dimensions. Only when I confirm, render the video using the project’s current iClone settings.” |
| Mocap | “Check whether iClone mocap is running; do not change or connect any device.” |

For a camera follow shot, use a real scene camera rather than the iClone
Preview Camera: “Create or activate `Camera1`, then key its transform at the
same frames as the subject, with a consistent relative offset.”

## Development

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
```

The main technical reference is the official [iClone 8 Python API
documentation](https://wiki.reallusion.com/IC8_Python_API).
