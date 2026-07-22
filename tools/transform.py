import math

import RLPy
from tools.objects import find_by_name


def get_transform(args):
    transform = find_by_name(args["name"]).LocalTransform()
    position, scale = transform.T(), transform.S()
    return {
        "name": args["name"],
        "position": {"x": position.x, "y": position.y, "z": position.z},
        "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
    }


def set_transform(args):
    obj = find_by_name(args["name"])
    current = obj.LocalTransform()
    pos, scale, rotation = current.T(), current.S(), current.R()
    if "position" in args:
        value = args["position"]
        pos = RLPy.RVector3(value.get("x", pos.x), value.get("y", pos.y), value.get("z", pos.z))
    if "scale" in args:
        value = args["scale"]
        scale = RLPy.RVector3(value.get("x", scale.x), value.get("y", scale.y), value.get("z", scale.z))
    if "rotation_degrees" in args:
        value = args["rotation_degrees"]
        matrix = RLPy.RMatrix3().FromEulerAngle(
            RLPy.EEulerOrder_XYZ,
            math.radians(value.get("x", 0)),
            math.radians(value.get("y", 0)),
            math.radians(value.get("z", 0)),
        )
        rotation = RLPy.RQuaternion()
        rotation.FromRotationMatrix(matrix)
    obj.GetControl("Transform").SetValue(RLPy.RGlobal.GetTime(), RLPy.RTransform(scale, rotation, pos))
    return get_transform({"name": obj.GetName()})


def delete_transform_key(args):
    obj = find_by_name(args["name"])
    control = obj.GetControl("Transform")
    if control is None:
        raise RuntimeError("Object has no animable Transform control")
    time = RLPy.RGlobal.GetFps().IndexedFrameTime(args["frame"])
    result = control.RemoveKey(time)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not remove transform key at frame %s" % args["frame"])
    return {"status": "ok", "name": obj.GetName(), "removed_frame": args["frame"]}


def register(registry):
    schema = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    registry["get_transform"] = {"handler": get_transform, "main_thread": True, "description": "Retourne position et échelle d'un objet.", "inputSchema": schema}
    registry["set_transform"] = {"handler": set_transform, "main_thread": True, "description": "Déplace, redimensionne et oriente un objet. rotation_degrees utilise des degrés.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "position": {"type": "object"}, "scale": {"type": "object"}, "rotation_degrees": {"type": "object"}}, "required": ["name"]}}
    registry["delete_transform_key"] = {"handler": delete_transform_key, "main_thread": True, "description": "Supprime une clé de transformation à une frame précise.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "frame": {"type": "integer", "minimum": 0}}, "required": ["name", "frame"]}}
