import os

import RLPy

from tools.objects import find_by_name


_PRIMITIVES = {
    "box": "Box.iProp",
    "ball": "Ball_000.iProp",
    "cone": "Cone_001.iProp",
    "cylinder": "Cylinder.iProp",
    "floor": "Floor_001.iProp",
    "torus": "Torus_001.iProp",
}


def _primitive_path(kind):
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    iclone_root = os.path.normpath(os.path.join(plugin_root, "..", "..", ".."))
    return os.path.join(iclone_root, "Program", "Assets", "ExternalFiles", "CreateObjectMenu", "StandardPrimitive", _PRIMITIVES[kind])


def _apply_options(obj, args):
    if args.get("name"):
        obj.SetName(args["name"])
    position = args.get("position")
    scale = args.get("scale")
    if position or scale:
        current = obj.LocalTransform()
        translation = RLPy.RVector3(position.get("x", 0), position.get("y", 0), position.get("z", 0)) if position else current.T()
        current_scale = RLPy.RVector3(scale.get("x", 1), scale.get("y", 1), scale.get("z", 1)) if scale else current.S()
        transform = RLPy.RTransform(current_scale, current.R(), translation)
        obj.GetControl("Transform").SetValue(RLPy.RGlobal.GetTime(), transform)


def create_primitive(args):
    kind = args.get("type", "box").lower()
    if kind not in _PRIMITIVES:
        raise ValueError("Unsupported primitive: %s" % kind)
    before = {obj.GetID() for obj in RLPy.RScene.FindObjects(RLPy.EObjectType_Prop)}
    path = _primitive_path(kind)
    if not os.path.isfile(path):
        raise FileNotFoundError("Primitive asset not found: %s" % path)
    if RLPy.RFileIO.LoadFile(path) != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not load primitive asset")
    imported = [obj for obj in RLPy.RScene.FindObjects(RLPy.EObjectType_Prop) if obj.GetID() not in before]
    if not imported:
        raise RuntimeError("Primitive loaded but no new prop was detected")
    obj = imported[-1]
    _apply_options(obj, args)
    return {"status": "ok", "name": obj.GetName(), "type": kind}


def save_project(args):
    path = args.get("path")
    result = RLPy.RFileIO.SaveProject(path) if path else RLPy.RFileIO.SaveProject()
    return {"status": "ok" if result == RLPy.RStatus.Success else "failed", "path": path}


def import_asset(args):
    path = args["path"]
    if not os.path.isfile(path):
        raise FileNotFoundError("Asset not found: %s" % path)
    result = RLPy.RFileIO.LoadFile(path)
    return {"status": "ok" if result == RLPy.RStatus.Success else "failed", "path": path}


def get_project_info(_args):
    fps = RLPy.RGlobal.GetFps()
    end = RLPy.RGlobal.GetEndTime()
    return {"fps": fps, "end_frame": RLPy.RTime.GetFrameIndex(end, fps), "object_count": len(RLPy.RScene.FindObjects(RLPy.EObjectType_Object))}


def load_motion(args):
    path = args["path"]
    if not os.path.isfile(path):
        raise FileNotFoundError("Motion file not found: %s" % path)
    obj = find_by_name(args["name"])
    time = RLPy.RTime.IndexedFrameTime(args.get("start_frame", 0), RLPy.RGlobal.GetFps())
    result = RLPy.RFileIO.LoadMotion(path, time, obj)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not load the motion onto this object")
    return {"status": "ok", "name": obj.GetName(), "path": path, "start_frame": args.get("start_frame", 0)}


def export_fbx(args):
    path = args["path"]
    parent = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(parent):
        raise FileNotFoundError("Export folder not found: %s" % parent)
    obj = find_by_name(args["name"]) if args.get("name") else None
    if obj is None:
        selected = RLPy.RScene.GetSelectedObjects()
        if len(selected) != 1:
            raise ValueError("name is required unless exactly one object is selected")
        obj = selected[0]
    result = RLPy.RFileIO.ExportFbxFile(
        obj, path,
        RLPy.EExportFbxOptions__None,
        RLPy.EExportFbxOptions2__None,
        RLPy.EExportFbxOptions3__None,
        RLPy.EExportTextureSize_Original,
        RLPy.EExportTextureFormat_Default,
        args.get("include_motion_path", ""),
    )
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not export FBX (the asset may require an export license)")
    return {"status": "ok", "name": obj.GetName(), "path": path}


def register(registry):
    registry["create_primitive"] = {"handler": create_primitive, "main_thread": True, "description": "Crée une primitive à partir des assets officiels iClone (Box, Ball, Cone, Cylinder, Floor, Torus).", "inputSchema": {"type": "object", "properties": {"type": {"type": "string", "enum": list(_PRIMITIVES)}, "name": {"type": "string"}, "position": {"type": "object"}, "scale": {"type": "object"}}}}
    registry["save_project"] = {"handler": save_project, "main_thread": True, "description": "Sauvegarde le projet iClone actuel.", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}}}
    registry["import_asset"] = {"handler": import_asset, "main_thread": True, "description": "Importe un fichier pris en charge par iClone (.iProp, .iAvatar, .fbx, etc.).", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}
    registry["get_project_info"] = {"handler": get_project_info, "main_thread": True, "description": "Retourne les informations du projet courant.", "inputSchema": {"type": "object", "properties": {}}}
    registry["load_motion"] = {"handler": load_motion, "main_thread": True, "description": "Charge un fichier de motion iClone sur un avatar ou prop à une frame donnée.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}, "start_frame": {"type": "integer", "minimum": 0}}, "required": ["name", "path"]}}
    registry["export_fbx"] = {"handler": export_fbx, "main_thread": True, "description": "Exporte un seul objet en FBX avec les réglages iClone documentés.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}, "include_motion_path": {"type": "string"}}, "required": ["path"]}}
