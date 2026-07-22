import RLPy


def _api_version(_args):
    return {"server": "mc-iclone8-mcp", "api": "iClone 8 RLPy", "python": "3.8+"}


def _ping(_args):
    return {"status": "ok"}


def _runtime_diagnostics(_args):
    time = RLPy.RGlobal.GetTime()
    fps = RLPy.RGlobal.GetFps()
    public = lambda value: sorted(name for name in dir(value) if not name.startswith("_"))
    return {
        "rtime_class_members": public(RLPy.RTime),
        "current_time_members": public(time),
        "fps_repr": repr(fps),
        "fps_members": public(fps),
        "time_repr": repr(time),
    }


def register(registry):
    registry["get_api_version"] = {"handler": _api_version, "description": "Retourne la version du serveur et la cible iClone 8.", "inputSchema": {"type": "object", "properties": {}}}
    registry["ping_iclone"] = {"handler": _ping, "description": "Vérifie que le pont MCP répond.", "inputSchema": {"type": "object", "properties": {}}}
    registry["get_runtime_diagnostics"] = {"handler": _runtime_diagnostics, "main_thread": True, "description": "Retourne les capacités RLPy réelles utiles au diagnostic, sans modifier la scène.", "inputSchema": {"type": "object", "properties": {}}}
