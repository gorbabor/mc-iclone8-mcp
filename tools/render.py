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
    registry["get_render_settings"] = {"handler": get_render_settings, "main_thread": True, "description": "Lit les dimensions des paramètres de rendu actuels d'iClone.", "inputSchema": {"type": "object", "properties": {}}}
    registry["render_video"] = {"handler": render_video, "main_thread": True, "description": "Lance le rendu vidéo avec les réglages actuels du projet iClone. Requiert une confirmation explicite.", "inputSchema": {"type": "object", "properties": {"confirm": {"type": "string", "description": "Valeur exacte : RENDER_VIDEO_WITH_CURRENT_SETTINGS"}}, "required": ["confirm"]}}
