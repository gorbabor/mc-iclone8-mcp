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


def _transform_control(name):
    obj = find_by_name(name)
    control = obj.GetControl("Transform")
    if control is None:
        raise RuntimeError("Object has no animable Transform control")
    return obj, control


def move_transform_key(args):
    obj, control = _transform_control(args["name"])
    fps = RLPy.RGlobal.GetFps()
    source = fps.IndexedFrameTime(args["frame"])
    offset = fps.IndexedFrameTime(args["offset_frames"])
    result = control.MoveKey(source, offset)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not move transform key")
    return {"status": "ok", "name": obj.GetName(), "frame": args["frame"], "offset_frames": args["offset_frames"]}


def set_transform_key_transition(args):
    obj, control = _transform_control(args["name"])
    transitions = {
        "linear": RLPy.ETransitionType_Linear,
        "step": RLPy.ETransitionType_Step,
        "ease_in": RLPy.ETransitionType_Ease_In,
        "ease_out": RLPy.ETransitionType_Ease_Out,
        "ease_in_out": RLPy.ETransitionType_Ease_In_Out,
    }
    transition = args.get("transition", "ease_in_out")
    if transition not in transitions:
        raise ValueError("Unsupported transition: %s" % transition)
    strength = float(args.get("strength", 50.0))
    if strength < 0 or strength > 100:
        raise ValueError("strength must be between 0 and 100")
    time = RLPy.RGlobal.GetFps().IndexedFrameTime(args["frame"])
    result = control.SetKeyTransition(time, transitions[transition], strength)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set transform key transition")
    return {"status": "ok", "name": obj.GetName(), "frame": args["frame"], "transition": transition, "strength": strength}


def clear_transform_keys(args):
    if args.get("confirm") != "DELETE_TRANSFORM_KEYS":
        raise ValueError("confirm must be DELETE_TRANSFORM_KEYS")
    obj, control = _transform_control(args["name"])
    result = control.ClearKeys()
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not clear transform keys")
    return {"status": "ok", "name": obj.GetName()}


def register(registry):
    schema = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    registry["get_transform"] = {"handler": get_transform, "main_thread": True, "description": "Retourne position et échelle d'un objet.", "inputSchema": schema}
    registry["set_transform"] = {"handler": set_transform, "main_thread": True, "description": "Déplace, redimensionne et oriente un objet. rotation_degrees utilise des degrés.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "position": {"type": "object"}, "scale": {"type": "object"}, "rotation_degrees": {"type": "object"}}, "required": ["name"]}}
    registry["delete_transform_key"] = {"handler": delete_transform_key, "main_thread": True, "description": "Supprime une clé de transformation à une frame précise.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "frame": {"type": "integer", "minimum": 0}}, "required": ["name", "frame"]}}
    registry["move_transform_key"] = {"handler": move_transform_key, "main_thread": True, "description": "Déplace une clé de transformation d’un décalage exprimé en frames.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "frame": {"type": "integer", "minimum": 0}, "offset_frames": {"type": "integer"}}, "required": ["name", "frame", "offset_frames"]}}
    registry["set_transform_key_transition"] = {"handler": set_transform_key_transition, "main_thread": True, "description": "Applique une interpolation à une clé de transformation.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "frame": {"type": "integer", "minimum": 0}, "transition": {"type": "string", "enum": ["linear", "step", "ease_in", "ease_out", "ease_in_out"]}, "strength": {"type": "number", "minimum": 0, "maximum": 100}}, "required": ["name", "frame"]}}
    registry["clear_transform_keys"] = {"handler": clear_transform_keys, "main_thread": True, "description": "Supprime toutes les clés de transformation d’un objet. Action destructive.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "confirm": {"type": "string", "enum": ["DELETE_TRANSFORM_KEYS"]}}, "required": ["name", "confirm"]}}
