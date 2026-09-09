import RLPy


def get_render_settings(_args):
    """Return the output dimensions from iClone's current render settings."""
    result = RLPy.RGlobal.GetScreenSize(0, 0)
    if not isinstance(result, (tuple, list)) or len(result) < 3:
        raise RuntimeError("Unexpected response from iClone render settings")
    if result[0] != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not read the render size")
    return {"width": int(result[1]), "height": int(result[2]), "note": "Other render options use the current iClone project settings."}


def render_video(args):
    """Start iClone's video rendering with its already configured project settings."""
    if args.get("confirm") != "RENDER_VIDEO_WITH_CURRENT_SETTINGS":
        raise ValueError("Set confirm to RENDER_VIDEO_WITH_CURRENT_SETTINGS to start rendering")
    result = RLPy.RGlobal.RenderVideo()
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not start video rendering")
    return {"status": "started", "message": "iClone started rendering with the current project render settings."}


def register(registry):
    registry["get_render_settings"] = {"handler": get_render_settings, "main_thread": True, "description": "Read the dimensions from iClone's current render settings.", "inputSchema": {"type": "object", "properties": {}}}
    registry["render_video"] = {"handler": render_video, "main_thread": True, "description": "Start video rendering with iClone's current project settings. Requires explicit confirmation.", "inputSchema": {"type": "object", "properties": {"confirm": {"type": "string", "description": "Exact value: RENDER_VIDEO_WITH_CURRENT_SETTINGS"}}, "required": ["confirm"]}}
