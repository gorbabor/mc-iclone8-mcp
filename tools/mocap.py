import RLPy


def get_mocap_status(_args):
    """Read the state of iClone's own motion-capture manager without changing it."""
    manager = RLPy.RGlobal.GetMocapManager()
    if manager is None:
        return {"available": False, "running": False}
    return {"available": True, "running": bool(manager.IsRunning())}


def get_network_capabilities(_args):
    """Report native iClone 8 TCP/UDP client availability for diagnostics."""
    return {
        "tcp_client": hasattr(RLPy, "RTcpClient"),
        "udp_client": hasattr(RLPy, "RUdpClient"),
        "note": "The MCP server itself already provides local HTTP control. Native TCP/UDP device bridges need a device-specific protocol and are intentionally not auto-connected.",
    }


def register(registry):
    registry["get_mocap_status"] = {"handler": get_mocap_status, "main_thread": True, "description": "Vérifie si le gestionnaire de motion capture d’iClone est disponible et en cours d’exécution.", "inputSchema": {"type": "object", "properties": {}}}
    registry["get_network_capabilities"] = {"handler": get_network_capabilities, "main_thread": True, "description": "Diagnostique la disponibilité des clients TCP et UDP natifs d’iClone 8, sans ouvrir de connexion.", "inputSchema": {"type": "object", "properties": {}}}
