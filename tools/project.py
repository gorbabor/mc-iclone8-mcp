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
    end_frame = fps.GetFrameIndex(end)
    return {"fps": fps.ToFloat(), "end_frame": end_frame, "object_count": len(RLPy.RScene.FindObjects(RLPy.EObjectType_Object))}


def load_motion(args):
    path = args["path"]
    if not os.path.isfile(path):
        raise FileNotFoundError("Motion file not found: %s" % path)
    obj = find_by_name(args["name"])
    time = RLPy.RGlobal.GetFps().IndexedFrameTime(args.get("start_frame", 0))
    result = RLPy.RFileIO.LoadMotion(path, time, obj)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not load the motion onto this object")
    return {"status": "ok", "name": obj.GetName(), "path": path, "start_frame": args.get("start_frame", 0)}


def preload_motion(args):
    path = args["path"]
    if not os.path.isfile(path):
        raise FileNotFoundError("Motion file not found: %s" % path)
    obj = find_by_name(args["name"])
    result = RLPy.RFileIO.PreLoadMotion(path, obj)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not pre-load the motion")
    return {"status": "ok", "name": obj.GetName(), "path": path}


def load_substance_painter_textures(args):
    path = args["path"]
    if not os.path.isdir(path):
        raise FileNotFoundError("Texture folder not found: %s" % path)
    obj = find_by_name(args["name"])
    method = getattr(RLPy.RFileIO, "LoadSubstancePainterTextures", None)
    if method is None:
        raise RuntimeError("This iClone installation does not expose Substance Painter texture loading")
    result = method(obj, path)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not load the Substance Painter textures")
    return {"status": "ok", "name": obj.GetName(), "path": path}


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


def _export_target(args):
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
    return obj, path


def _status_result(result, operation):
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not %s" % operation)
    return {"status": "ok"}


def export_obj(args):
    obj, path = _export_target(args)
    method = getattr(RLPy.RFileIO, "ExportObjFile", None)
    if method is None:
        raise RuntimeError("ExportObjFile is not exposed by this iClone 8 build")
    option_name = args.get("option", "EExportObjOptions_None")
    option = getattr(RLPy, option_name, None)
    if option is None:
        raise ValueError("Unknown OBJ export option: %s" % option_name)
    result = method(obj, path, option)
    response = _status_result(result, "export OBJ")
    response.update({"name": obj.GetName(), "path": path, "experimental": True, "limitation": "The official API documents this operation for Character Creator 3; verify behavior in iClone 8."})
    return response


def export_glb(args):
    obj, path = _export_target(args)
    method = getattr(RLPy.RFileIO, "ExportGlbFile", None)
    setting_type = getattr(RLPy, "RExportGlbSetting", None)
    if method is None or setting_type is None:
        raise RuntimeError("GLB export is not exposed by this iClone 8 build")
    setting = setting_type()
    option = args.get("option", "")
    result = method(obj, path, setting, option)
    response = _status_result(result, "export GLB")
    response.update({"name": obj.GetName(), "path": path, "experimental": True})
    return response


def load_object(args):
    path = args["path"]
    if not os.path.isfile(path):
        raise FileNotFoundError("Object file not found: %s" % path)
    method = getattr(RLPy.RFileIO, "LoadObject", None)
    if method is None:
        raise RuntimeError("LoadObject is not exposed by this iClone 8 build")
    obj = method(path, bool(args.get("record_step", True)))
    if obj is None:
        raise RuntimeError("iClone did not return the loaded object")
    return {"status": "ok", "name": obj.GetName(), "type": obj.GetType().ToString() if hasattr(obj.GetType(), "ToString") else str(obj.GetType()), "path": path, "experimental": True}


def load_alembic(args):
    path = args["path"]
    if not os.path.isfile(path):
        raise FileNotFoundError("Alembic file not found: %s" % path)
    selected = RLPy.RScene.GetSelectedObjects()
    if len(selected) != 1:
        raise ValueError("Select exactly one target object before loading Alembic")
    axis_name = args.get("up_axis", "ECoordinateAxis_Y")
    axis = getattr(RLPy, axis_name, None)
    if axis is None:
        raise ValueError("Unknown Alembic up axis: %s" % axis_name)
    method = getattr(RLPy.RFileIO, "LoadAlembicFile", None)
    if method is None:
        raise RuntimeError("LoadAlembicFile is not exposed by this iClone 8 build")
    response = _status_result(method(selected[0], path, axis), "load Alembic")
    response.update({"name": selected[0].GetName(), "path": path, "experimental": True})
    return response


def save_thumbnail(args):
    source = args["source"]
    destination = args["destination"]
    if not os.path.isfile(source):
        raise FileNotFoundError("iClone file not found: %s" % source)
    parent = os.path.dirname(os.path.abspath(destination))
    if not os.path.isdir(parent):
        raise FileNotFoundError("Thumbnail folder not found: %s" % parent)
    method = getattr(RLPy.RFileIO, "SaveThumbnailToFile", None)
    if method is None:
        raise RuntimeError("SaveThumbnailToFile is not exposed by this iClone 8 build")
    response = _status_result(method(source, destination), "save thumbnail")
    response.update({"source": source, "destination": destination})
    return response


def register(registry):
    registry["create_primitive"] = {"handler": create_primitive, "main_thread": True, "description": "Create a primitive from the official iClone assets (Box, Ball, Cone, Cylinder, Floor, Torus).", "inputSchema": {"type": "object", "properties": {"type": {"type": "string", "enum": list(_PRIMITIVES)}, "name": {"type": "string"}, "position": {"type": "object"}, "scale": {"type": "object"}}}}
    registry["save_project"] = {"handler": save_project, "main_thread": True, "description": "Save the current iClone project.", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}}}
    registry["import_asset"] = {"handler": import_asset, "main_thread": True, "description": "Import a file supported by iClone (.iProp, .iAvatar, .fbx, etc.).", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}
    registry["get_project_info"] = {"handler": get_project_info, "main_thread": True, "description": "Return information about the current project.", "inputSchema": {"type": "object", "properties": {}}}
    registry["load_motion"] = {"handler": load_motion, "main_thread": True, "description": "Load an iClone motion file onto an avatar or prop at a given frame.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}, "start_frame": {"type": "integer", "minimum": 0}}, "required": ["name", "path"]}}
    registry["preload_motion"] = {"handler": preload_motion, "main_thread": True, "description": "Preload a motion file to speed up applying it later to an avatar or prop.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}}, "required": ["name", "path"]}}
    registry["load_substance_painter_textures"] = {"handler": load_substance_painter_textures, "main_thread": True, "description": "Load textures exported from Substance Painter onto an object, from a local folder.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}}, "required": ["name", "path"]}}
    registry["export_fbx"] = {"handler": export_fbx, "main_thread": True, "description": "Export a single object to FBX with the documented iClone settings.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}, "include_motion_path": {"type": "string"}}, "required": ["path"]}}
    registry["export_obj"] = {"handler": export_obj, "main_thread": True, "description": "Export an object to OBJ (experimental API, documented mainly for Character Creator 3).", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}, "option": {"type": "string"}}, "required": ["path"]}}
    registry["export_glb"] = {"handler": export_glb, "main_thread": True, "description": "Export an object to GLB via RExportGlbSetting (experimental API).", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path": {"type": "string"}, "option": {"type": "string"}}, "required": ["path"]}}
    registry["load_object"] = {"handler": load_object, "main_thread": True, "description": "Load an iClone object and return the created object (experimental API).", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "record_step": {"type": "boolean"}}, "required": ["path"]}}
    registry["load_alembic"] = {"handler": load_alembic, "main_thread": True, "description": "Load an Alembic animation onto the selected object (experimental API).", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "up_axis": {"type": "string", "enum": ["ECoordinateAxis_X", "ECoordinateAxis_NegativeX", "ECoordinateAxis_Y", "ECoordinateAxis_NegativeY", "ECoordinateAxis_Z", "ECoordinateAxis_NegativeZ"]}}, "required": ["path"]}}
    registry["save_thumbnail"] = {"handler": save_thumbnail, "main_thread": True, "description": "Extract a thumbnail from an iClone file to an image.", "inputSchema": {"type": "object", "properties": {"source": {"type": "string"}, "destination": {"type": "string"}}, "required": ["source", "destination"]}}
