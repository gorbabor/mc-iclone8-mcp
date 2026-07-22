import json
import os
import threading

rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}

try:
    import RLPy
    from PySide2 import QtCore, QtWidgets
    QtCore.QStringListModel
    from shiboken2 import wrapInstance
    _ICLONE_AVAILABLE = True
except ImportError:
    RLPy = None
    QtCore = QtWidgets = wrapInstance = None
    _ICLONE_AVAILABLE = False

_server = None
_dialog = None
_callbacks = []
_lock = threading.RLock()


def _config():
    try:
        with open(os.path.join(os.path.dirname(__file__), "mcp_config.json"), "r") as stream:
            return json.load(stream)
    except Exception:
        return {"server": {"host": "127.0.0.1", "port": 8766}}


def _tool_registry():
    # Features are registered in small, auditable modules as they are validated.
    from tools import avatar, camera, core, lights, materials, morphs, project, scene, timeline, transform
    tools = {}
    core.register(tools)
    scene.register(tools)
    project.register(tools)
    transform.register(tools)
    materials.register(tools)
    timeline.register(tools)
    camera.register(tools)
    lights.register(tools)
    avatar.register(tools)
    morphs.register(tools)
    return tools


def start_server():
    global _server
    with _lock:
        if _server and _server.running:
            return "http://%s:%d/mcp" % (_server.host, _server.port)
        from dispatch import start as start_dispatch
        from mcp_handler import MCPHandler
        from server import MCPServer
        start_dispatch()
        config = _config()["server"]
        candidate = MCPServer(MCPHandler(_tool_registry()), config["host"], config["port"])
        candidate.start()
        _server = candidate
        return "http://%s:%d/mcp" % (candidate.host, candidate.port)


def stop_server():
    global _server
    with _lock:
        candidate, _server = _server, None
        if candidate:
            candidate.stop()
            return True
        return False


if _ICLONE_AVAILABLE:
    class DialogCallback(RLPy.RDialogCallback):
        def __init__(self):
            RLPy.RDialogCallback.__init__(self)

        def OnDialogClose(self):
            global _dialog
            _dialog = None
            try:
                threading.Thread(target=stop_server, name="mc-iclone8-mcp-stop", daemon=True).start()
            except Exception as error:
                print("mc-iclone8-mcp close error: %s" % error)
            return True


def show_dialog():
    global _dialog
    if not _ICLONE_AVAILABLE:
        raise RuntimeError("mc-iclone8-mcp doit être chargé dans iClone 8")
    if _dialog is not None:
        _dialog.Show()
        return
    _dialog = RLPy.RUi.CreateRDialog()
    _dialog.SetWindowTitle("mc-iclone8-mcp")
    callback = DialogCallback()
    _callbacks.append(callback)
    _dialog.RegisterEventCallback(callback)
    dialog = wrapInstance(int(_dialog.GetWindow()), QtWidgets.QDialog)
    layout = dialog.layout()
    label = QtWidgets.QLabel("Serveur MCP iClone 8\nPort 8766\nAPI documentée et commandes exécutées dans le thread iClone.")
    layout.addWidget(label)
    status = QtWidgets.QLabel("STATUT : arrêté")
    layout.addWidget(status)
    start_button = QtWidgets.QPushButton("Démarrer")
    stop_button = QtWidgets.QPushButton("Arrêter")
    layout.addWidget(start_button)
    layout.addWidget(stop_button)

    def start_from_ui():
        try:
            status.setText("STATUT : en écoute sur " + start_server())
        except Exception as error:
            status.setText("STATUT : erreur - " + str(error))

    def stop_from_ui():
        status.setText("STATUT : arrêté" if stop_server() else "STATUT : déjà arrêté")

    start_button.clicked.connect(start_from_ui)
    stop_button.clicked.connect(stop_from_ui)
    _dialog.Show()


def initialize_plugin():
    if not _ICLONE_AVAILABLE:
        raise RuntimeError("mc-iclone8-mcp doit être chargé dans iClone 8")
    main_window = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)
    menu = main_window.menuBar().findChild(QtWidgets.QMenu, "mc_iclone8_mcp_menu")
    if menu is None:
        menu = wrapInstance(int(RLPy.RUi.AddMenu("mc-iclone8-mcp", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        menu.setObjectName("mc_iclone8_mcp_menu")
    action = menu.addAction("Ouvrir le serveur MCP")
    action.triggered.connect(show_dialog)


def run_script():
    if not _ICLONE_AVAILABLE:
        raise RuntimeError("mc-iclone8-mcp doit être chargé dans iClone 8")
    initialize_plugin()
