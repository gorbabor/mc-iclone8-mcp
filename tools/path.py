import math

import RLPy

from tools.objects import find_by_name
from tools.common import current_frame, frame_time, require_success, require_unit_interval, rl_string


def _path_control(obj, key):
    control = obj.GetControl(key)
    if control is None:
        raise RuntimeError("Object %s has no %s control; attach it to a path first" % (obj.GetName(), key))
    return control


def list_paths(_args):
    if not hasattr(RLPy, "EObjectType_Path"):
        return {"paths": [], "supported": False}
    paths = RLPy.RScene.FindObjects(RLPy.EObjectType_Path)
    return {"supported": True, "paths": [{"id": path.GetID(), "name": path.GetName()} for path in paths]}


def get_path_info(args):
    """Inspect path controls and the currently linked path without mutating the scene."""
    obj = find_by_name(args["name"])
    frame = int(args.get("frame", current_frame()))
    time = frame_time(frame)
    linked = obj.GetLinkedObject(time)
    maximum = RLPy.RVector3()
    center = RLPy.RVector3()
    minimum = RLPy.RVector3()
    bounds_status = obj.GetBounds(maximum, center, minimum)
    return {
        "name": obj.GetName(),
        "type": rl_string(obj.GetType()),
        "frame": frame,
        "linked_path": linked.GetName() if linked is not None else None,
        "controls": {
            "PathPosition": obj.GetControl("PathPosition") is not None,
            "PathOffset": obj.GetControl("PathOffset") is not None,
        },
        "bounds": {
            "status": "ok" if bounds_status == RLPy.RStatus.Success else "failed",
            "min": {"x": minimum.x, "y": minimum.y, "z": minimum.z},
            "center": {"x": center.x, "y": center.y, "z": center.z},
            "max": {"x": maximum.x, "y": maximum.y, "z": maximum.z},
        },
    }


def follow_path(args):
    obj = find_by_name(args["name"])
    path = find_by_name(args["path_name"])
    frame = int(args.get("frame", RLPy.RGlobal.GetFps().GetFrameIndex(RLPy.RGlobal.GetTime())))
    result = obj.FollowPath(path, frame_time(frame))
    require_success(result, "iClone could not attach %s to path %s" % (obj.GetName(), path.GetName()))
    return {"status": "ok", "name": obj.GetName(), "path_name": path.GetName(), "frame": frame}


def release_path(args):
    obj = find_by_name(args["name"])
    frame = int(args.get("frame", RLPy.RGlobal.GetFps().GetFrameIndex(RLPy.RGlobal.GetTime())))
    result = obj.ReleasePath(frame_time(frame))
    require_success(result, "iClone could not release the path from %s" % obj.GetName())
    return {"status": "ok", "name": obj.GetName(), "frame": frame}


def set_path_position(args):
    obj = find_by_name(args["name"])
    frame = int(args.get("frame", RLPy.RGlobal.GetFps().GetFrameIndex(RLPy.RGlobal.GetTime())))
    position = float(args["position"])
    position = require_unit_interval(position, "position")
    control = _path_control(obj, "PathPosition")
    result = control.SetValue(frame_time(frame), position)
    require_success(result, "iClone could not set PathPosition")
    return {"status": "ok", "name": obj.GetName(), "position": position, "frame": frame}


def set_path_offset(args):
    obj = find_by_name(args["name"])
    frame = int(args.get("frame", RLPy.RGlobal.GetFps().GetFrameIndex(RLPy.RGlobal.GetTime())))
    value = args.get("position", {})
    rotation = args.get("rotation_degrees", {})
    matrix = RLPy.RMatrix3().FromEulerAngle(
        RLPy.EEulerOrder_XYZ,
        math.radians(rotation.get("x", 0)),
        math.radians(rotation.get("y", 0)),
        math.radians(rotation.get("z", 0)),
    )
    quaternion = RLPy.RQuaternion()
    quaternion.FromRotationMatrix(matrix)
    transform = RLPy.RTransform(
        RLPy.RVector3(1, 1, 1),
        quaternion,
        RLPy.RVector3(value.get("x", 0), value.get("y", 0), value.get("z", 0)),
    )
    control = _path_control(obj, "PathOffset")
    result = control.SetValue(frame_time(frame), transform)
    require_success(result, "iClone could not set PathOffset")
    return {"status": "ok", "name": obj.GetName(), "position": value, "rotation_degrees": rotation, "frame": frame}


def clear_path_keys(args):
    if args.get("confirm") != "DELETE_PATH_KEYS":
        raise ValueError("confirm must be DELETE_PATH_KEYS")
    obj = find_by_name(args["name"])
    cleared = []
    for key in ("PathPosition", "PathOffset"):
        control = obj.GetControl(key)
        if control is not None:
            result = control.ClearKeys()
            if result != RLPy.RStatus.Success:
                raise RuntimeError("iClone could not clear %s keys" % key)
            cleared.append(key)
    return {"status": "ok", "name": obj.GetName(), "cleared_controls": cleared}


def register(registry):
    registry["list_paths"] = {"handler": list_paths, "main_thread": True, "description": "List the iClone 8 paths present in the scene.", "inputSchema": {"type": "object", "properties": {}}}
    registry["get_path_info"] = {"handler": get_path_info, "main_thread": True, "description": "Inspect an object's linked path, controls and bounds.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "frame": {"type": "integer", "minimum": 0}}, "required": ["name"]}}
    registry["follow_path"] = {"handler": follow_path, "main_thread": True, "description": "Attach an existing object to an iClone path at a given frame.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "path_name": {"type": "string"}, "frame": {"type": "integer", "minimum": 0}}, "required": ["name", "path_name"]}}
    registry["release_path"] = {"handler": release_path, "main_thread": True, "description": "Release an object from its iClone path.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "frame": {"type": "integer", "minimum": 0}}, "required": ["name"]}}
    registry["set_path_position"] = {"handler": set_path_position, "main_thread": True, "description": "Set an object's normalized position on its path between 0 and 1.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "position": {"type": "number", "minimum": 0, "maximum": 1}, "frame": {"type": "integer", "minimum": 0}}, "required": ["name", "position"]}}
    registry["set_path_offset"] = {"handler": set_path_offset, "main_thread": True, "description": "Set the position/rotation offset of an object attached to a path.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "position": {"type": "object"}, "rotation_degrees": {"type": "object"}, "frame": {"type": "integer", "minimum": 0}}, "required": ["name"]}}
    registry["clear_path_keys"] = {"handler": clear_path_keys, "main_thread": True, "description": "Remove an object's PathPosition and PathOffset keys. Destructive action.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "confirm": {"type": "string", "enum": ["DELETE_PATH_KEYS"]}}, "required": ["name", "confirm"]}}
