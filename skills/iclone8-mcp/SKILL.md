---
name: iclone8-mcp
description: Expert workflow for controlling iClone 8 through the mc-iclone8-mcp Streamable HTTP server. Use when an agent must create or inspect scenes, props, avatars, materials, lights, cameras, animations, morphs, motions, imports, exports, or renders in iClone 8, or when it must turn a natural-language 3D request into a safe, verifiable MCP tool sequence.
---

# iClone 8 MCP expert

Use this skill to turn a 3D objective into a deliberate iClone 8 operation. The MCP server is local and must already be running at `http://127.0.0.1:8766/mcp`.

## Operating rules

1. Start with `ping_iclone`, `get_api_version`, and, when the task is complex, `get_project_info` and `get_timeline`.
2. Inspect before mutating: use `list_objects`, `get_selection`, capability tools, and material/morph queries before guessing names or indices.
3. Use exact object names, frame numbers, units, colors in RGB 0–1, and explicit camera names.
4. For destructive operations require confirmation in the user request and pass the exact confirmation token required by the tool.
5. Execute in small stages: create/import, configure, animate, camera, render. Verify each stage with a read tool.
6. Never claim that a render, animation, or color change succeeded without checking the resulting state.
7. Use a real scene camera for animation. The iClone Preview Camera cannot be transform-animated.
8. For humanoid movement, prefer native iClone skeletal motions over root-transform displacement.
9. Preserve each avatar's existing anchor position. Removing an animation must never become an unintended relocation.
10. Keep the MCP server local. Do not expose port 8766 externally or invent TCP/UDP device protocols.

## Tool selection map

- Diagnostics: `ping_iclone`, `get_api_version`, `get_runtime_diagnostics`.
- Scene: `list_objects`, `get_selection`, `select_object`, `set_visibility`, `delete_object`, `clone_object`, `link_object`, `unlink_object`, `align_object`, `set_static`.
- Creation and files: `create_primitive`, `save_project`, `get_project_info`, `import_asset`, `load_motion`, `preload_motion`, `load_substance_painter_textures`, `export_fbx`.
- Object animation: `get_transform`, `set_transform`, `delete_transform_key`, `move_transform_key`, `set_transform_key_transition`, `clear_transform_keys`.
- Timeline: `get_timeline`, `set_timeline`, `play_timeline`, `pause_timeline`, `stop_timeline`, `clear_scene_animations`.
- Cameras: `get_camera`, `get_camera_capabilities`, `set_camera`, `set_camera_transform`, `set_camera_focal_key`, `set_camera_dof`, `set_current_camera`, `set_camera_look_at`.
- Materials: `get_materials`, `set_material_color`, `set_material_texture`, `set_material_value`.
- Lights: `get_light`, `set_light`.
- Avatars: `get_avatar_info`, `get_avatar_capabilities`, `get_skin_bones`, `get_animation_clips`, `set_clip_speed`, `set_clip_loop_count`.
- Morphs: `list_morphs`, `get_morph_weight`, `set_morph_weight`.
- Rendering: `get_render_settings`, `render_video`.
- Mocap/network diagnostics: `get_mocap_status`, `get_network_capabilities`.

## Reliable workflows

### Build a scene

1. Inspect the project and object list.
2. Create primitives or import assets with stable names.
3. Set transforms and materials.
4. Verify object names, locations, scales, and material values.
5. Save only when the user asks or confirms a save path.

### Animate an object

1. Read the timeline and choose explicit frames.
2. At each frame, call `set_timeline`, then `set_transform`.
3. Apply `set_transform_key_transition` where interpolation matters.
4. Read the timeline and inspect transforms at representative frames.
5. Play the range only after the keys are verified.

### Animate a humanoid naturally

Use this workflow for conversation, walking, gesturing, reacting, or idle
behavior. Do not simulate a person talking by moving the avatar root back and
forth.

1. Verify the target names with `list_objects` using `type: "avatar"`.
2. Inspect each avatar with `get_avatar_info` and `get_avatar_capabilities`.
   Require a skeleton and report the available face, viseme, morph, HIK, and
   physics components. The current MCP does not expose a dedicated Persona
   object query, so do not claim a Persona was found unless a future tool
   returns it explicitly.
3. Inspect existing clips with `get_animation_clips`. Preserve a useful clip
   when it already contains the requested behavior.
4. Search the installed iClone asset library for suitable native motions before
   inventing keys. Prefer these categories and examples:
   - conversation: `Base Motion\Talk\01_Talk.iMotion`, `02_Talk.iMotion`;
   - explanation: `01_Explain1.iMotion`, `01_Explain2.iMotion`,
     `01_Explain3.iMotion`;
   - disagreement/reaction: `02_Argue 1.iMotion`, `02_Argue 2.iMotion`;
   - subtle behavior: `Base Motion\Idle\01_Natural.iMotion`,
     `02_Natural.iMotion`, `01_Look Around.iMotion`.
5. Before changing animation, read and store each avatar's position and scale at
   the requested start frame. Treat these values as the immutable scene anchor.
6. If earlier experimentation created root transform keys that merely move the
   avatar, stop the timeline and clear those object-animation keys with
   `clear_transform_keys` and the required confirmation token. Immediately
   restore the stored anchor with `set_transform` at the start frame. Do not
   move the avatar to a new conversation point and do not clear the avatar's
   static placement.
7. Apply motions with `load_motion` at the requested start frame. Use different
   but compatible Talk/Explain motions for two speakers when available so they
   do not mirror each other mechanically.
8. Use `set_clip_speed` and `set_clip_loop_count` only after checking the clip
   duration and requested frame range. Do not assume that loop count 0 means
   infinite playback.
9. Verify the result with `get_animation_clips`, `get_transform` at the start
   frame, and `get_timeline`, then play the
   requested range. If only transform tools are available and no suitable
   motion file exists, clearly label root motion as a fallback, keep it subtle,
   and do not describe it as arm/hand/body gesture animation.

### Animate and film with a camera

1. Find a real camera with `list_objects` and check it with `get_camera_capabilities`.
2. Set the camera transform at several frames with `set_camera_transform`.
3. Aim it with `set_camera_look_at` toward the subject at the same frames.
4. Add focal and DOF keys only when requested; keep focus and range consistent with the subject.
5. Activate it with `set_current_camera`, verify it, then render only after explicit confirmation.

### Apply a visible color

1. Call `get_materials` to identify the correct material index.
2. Use `set_material_color` with normalized RGB values, for example red = `{"r":1,"g":0,"b":0}`.
3. Leave `override_diffuse_texture` enabled when a texture would hide the color.
4. Call `get_materials` again to verify the diffuse color.

### Avatar and facial work

1. Call `get_avatar_info` and `get_avatar_capabilities` first.
2. Use `get_skin_bones` and `get_animation_clips` for inspection.
3. Load a motion or adjust an existing clip; use speed and loop tools for playback changes.
4. For morphs, list names and meshes before reading or writing a weight.
5. Report unavailable components instead of fabricating support.

## Prompt contract

Rewrite an underspecified user request into this internal structure before calling tools:

```text
OBJECTIVE: one observable final result
SCENE: objects/assets to create or use, with stable names
ANIMATION: frame range, preferred native motion files, clips, key frames only when needed, interpolation
CAMERA: real camera name, path, target, focal length, DOF, render view
MATERIALS: object, material index, RGB/texture/channel/value
OUTPUT: save path, export path, or render request
SAFETY: destructive actions requiring confirmation
VERIFICATION: readbacks that prove each requested result
```

If information is missing, infer only harmless defaults and state them. Ask for clarification when the missing value changes the scene materially, such as the asset path, target object, frame range, or render output path.

## Example prompt format

```text
Using mc-iclone8-mcp, create a small red sphere named Orbit_Sphere and a cube named Center_Cube.
Place the cube at (0, 0, 0), the sphere at (300, 0, 100), and animate the sphere on a vertical ellipse
from frame 0 to 1799 for three complete revolutions. Use the real camera Camera1, keep the sphere in
frame with smooth camera motion, activate Camera1, verify representative frames, and do not render yet.
Report every tool result and any limitation.
```

## Failure handling

- If `ping_iclone` fails, do not retry scene mutations; ask the user to load the plugin and start the server.
- If an object or camera is not found, list the scene and use the exact returned name.
- If a humanoid has no suitable native motion, do not fake conversation with large root translations; report the limitation and use only a subtle fallback if the user accepts it.
- If a camera transform is not animable, switch to a real scene camera and explain why.
- If a material color is not visible, inspect materials and override the diffuse texture.
- If a motion, texture, or FBX path fails, verify the path exists and report the iClone/API limitation.
- If a tool returns an API error, preserve the error text, stop the dependent sequence, and do not claim completion.
