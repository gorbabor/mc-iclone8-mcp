import os

import RLPy


def _call(name, default=None):
    method = getattr(RLPy.RApplication, name, None)
    if method is None:
        return default
    try:
        value = method()
        return value.ToString() if hasattr(value, "ToString") else str(value)
    except Exception:
        return default


def _content_parent(args):
    parent = args.get("parent") or _call("GetDefaultContentFolder")
    if not parent or not isinstance(parent, str) or not os.path.isdir(parent):
        raise FileNotFoundError("Content folder not found: %s" % parent)
    return parent


def get_application_info(_args):
    """Return read-only host information, without relying on iClone 7 APIs."""
    return {
        "application": "iClone",
        "supported_api": "iClone 8 Python API",
        "api_version": _call("GetApiVersion"),
        "product_name": _call("GetProductName"),
        "product_version": _call("GetProductVersion"),
        "program_path": _call("GetProgramPath"),
        "custom_data_path": _call("GetCustomDataPath"),
        "custom_content_folder": _call("GetCustomContentFolder"),
        "default_content_folder": _call("GetDefaultContentFolder"),
        "default_project_path": _call("GetDefaultProjectPath"),
    }


def list_content_folders(args):
    parent = _content_parent(args)
    method = getattr(RLPy.RApplication, "GetContentFoldersInFolder", None)
    if method is None:
        raise RuntimeError("GetContentFoldersInFolder is not exposed by this iClone 8 build")
    values = method(parent)
    return {"parent": parent, "folders": [str(value) for value in values]}


def list_content_files(args):
    parent = _content_parent(args)
    method = getattr(RLPy.RApplication, "GetContentFilesInFolder", None)
    if method is None:
        raise RuntimeError("GetContentFilesInFolder is not exposed by this iClone 8 build")
    values = method(parent)
    return {"parent": parent, "files": [str(value) for value in values]}


def register(registry):
    registry["get_application_info"] = {"handler": get_application_info, "main_thread": True, "description": "Return version and path information for the iClone 8 installation.", "inputSchema": {"type": "object", "properties": {}}}
    registry["list_content_folders"] = {"handler": list_content_folders, "main_thread": True, "description": "List iClone content subfolders from the Smart Content Manager API.", "inputSchema": {"type": "object", "properties": {"parent": {"type": "string"}}}}
    registry["list_content_files"] = {"handler": list_content_files, "main_thread": True, "description": "List iClone content files from the Smart Content Manager API.", "inputSchema": {"type": "object", "properties": {"parent": {"type": "string"}}}}
