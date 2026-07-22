import RLPy


def _api_version(_args):
    return {"server": "mc-iclone8-mcp", "api": "iClone 8 RLPy", "python": "3.8+"}


def _ping(_args):
    return {"status": "ok"}


def register(registry):
    registry["get_api_version"] = {"handler": _api_version, "description": "Retourne la version du serveur et la cible iClone 8.", "inputSchema": {"type": "object", "properties": {}}}
    registry["ping_iclone"] = {"handler": _ping, "description": "Vérifie que le pont MCP répond.", "inputSchema": {"type": "object", "properties": {}}}
