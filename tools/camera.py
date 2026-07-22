import RLPy

from tools.objects import find_by_name


def _find(name=None):
    current = RLPy.RScene.GetCurrentCamera()
    if name and current is not None and current.GetName() == name:
        return current
    camera = RLPy.RScene.FindObject(RLPy.EObjectType_Camera, name) if name else current
    if camera is None:
        raise ValueError("Camera not found")
    return camera


def _transform_control(camera):
    control = camera.GetControl("Transform")
    if control is None:
        raise RuntimeError(
            "Camera '%s' has no animable Transform control. "
            "The iClone Preview Camera cannot be animated; use a real scene camera." % camera.GetName()
        )
    return control


def get_camera(args):
    camera = _find(args.get("name"))
    time = RLPy.RGlobal.GetTime()
    return {"name": camera.GetName(), "focal_length": camera.GetFocalLength(time), "angle_of_view": camera.GetAngleOfView(time), "near_clipping_plane": camera.GetNearClippingPlane(), "far_clipping_plane": camera.GetFarClippingPlane()}


def set_camera(args):
    camera = _find(args.get("name"))
    time = RLPy.RGlobal.GetTime()
    if "focal_length" in args and camera.SetFocalLength(time, args["focal_length"]) != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set focal length")
    if "near_clipping_plane" in args and camera.SetNearClippingPlane(args["near_clipping_plane"]) != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set near clipping plane")
    if "far_clipping_plane" in args and camera.SetFarClippingPlane(args["far_clipping_plane"]) != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set far clipping plane")
    return get_camera({"name": camera.GetName()})


def get_camera_capabilities(args):
    camera = _find(args.get("name"))
    control = camera.GetControl("Transform")
    dof = camera.GetDOFData()
    focal_count = camera.GetFocalLengthKeyCount() if hasattr(camera, "GetFocalLengthKeyCount") else None
    dof_count = camera.GetDofKeyCount() if hasattr(camera, "GetDofKeyCount") else None
    look_at = camera.IsLookAtMode(RLPy.RGlobal.GetTime()) if hasattr(camera, "IsLookAtMode") else None
    return {
        "name": camera.GetName(),
        "transform_animable": control is not None,
        "dof_available": dof is not None,
        "focal_length_keys": focal_count,
        "dof_keys": dof_count,
        "is_look_at_mode": bool(look_at) if look_at is not None else None,
        "preview_camera_note": "A real scene camera is required for transform animation.",
    }


def set_camera_transform(args):
    camera = _find(args.get("name"))
    control = _transform_control(camera)
    current = camera.LocalTransform()
    position, scale, rotation = current.T(), current.S(), current.R()
    if "position" in args:
        value = args["position"]
        position = RLPy.RVector3(value.get("x", position.x), value.get("y", position.y), value.get("z", position.z))
    if "rotation_degrees" in args:
        import math
        value = args["rotation_degrees"]
        matrix = RLPy.RMatrix3().FromEulerAngle(RLPy.EEulerOrder_XYZ, math.radians(value.get("x", 0)), math.radians(value.get("y", 0)), math.radians(value.get("z", 0)))
        rotation = RLPy.RQuaternion()
        rotation.FromRotationMatrix(matrix)
    result = control.SetValue(RLPy.RGlobal.GetTime(), RLPy.RTransform(scale, rotation, position))
    camera.Update()
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set the camera transform")
    return {"status": "ok", "name": camera.GetName(), "position": {"x": position.x, "y": position.y, "z": position.z}}


def set_camera_focal_key(args):
    camera = _find(args.get("name"))
    result = camera.SetFocalLength(RLPy.RGlobal.GetTime(), float(args["focal_length"]))
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set camera focal length")
    return get_camera({"name": camera.GetName()})


def set_camera_dof(args):
    camera = _find(args.get("name"))
    data = RLPy.RCameraDofData()
    data.SetEnable(bool(args.get("enabled", True)))
    data.SetFocus(float(args.get("focus", 200)))
    data.SetRange(float(args.get("range", 100)))
    key = RLPy.RKey()
    key.SetTime(RLPy.RGlobal.GetTime())
    key.SetTransitionType(RLPy.ETransitionType_Linear)
    key.SetTransitionStrength(float(args.get("strength", 50)))
    result = camera.AddDofKey(key, data)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not add camera DOF key")
    return {"status": "ok", "name": camera.GetName(), "enabled": bool(args.get("enabled", True)), "focus": float(args.get("focus", 200)), "range": float(args.get("range", 100))}


def set_current_camera(args):
    camera = _find(args["name"])
    result = RLPy.RScene.SetCurrentCamera(camera)
    if result is not None and result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not activate camera")
    return {"status": "ok", "name": camera.GetName()}


def set_camera_look_at(args):
    camera = _find(args.get("name"))
    target = find_by_name(args["target_name"])
    view_position = camera.WorldTransform().T()
    view_target = target.WorldTransform().T()
    forward = view_position - view_target
    forward.Normalize()
    up_axis = RLPy.RVector3(RLPy.RVector3.UNIT_Z)
    right = up_axis.Cross(forward)
    right.Normalize()
    up = forward.Cross(right)
    orientation = RLPy.RMatrix3(
        right.x, right.y, right.z,
        up.x, up.y, up.z,
        forward.x, forward.y, forward.z,
    )
    rotation = orientation.ToEulerAngle(RLPy.EEulerOrder_XYZ, 0, 0, 0)
    control = _transform_control(camera)
    block = control.GetDataBlock()
    time = RLPy.RGlobal.GetTime()
    for axis, value in zip(("X", "Y", "Z"), rotation):
        block.SetData("Rotation/Rotation" + axis, time, RLPy.RVariant(value))
    camera.Update()
    return {"status": "ok", "camera": camera.GetName(), "target": target.GetName()}


def register(registry):
    registry["get_camera"] = {"handler": get_camera, "main_thread": True, "description": "Lit les paramètres de la caméra active ou nommée.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}}}
    registry["get_camera_capabilities"] = {"handler": get_camera_capabilities, "main_thread": True, "description": "Diagnostique les capacités d’une caméra iClone 8 avant de l’animer.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}}}
    registry["set_camera"] = {"handler": set_camera, "main_thread": True, "description": "Modifie focale et plans de clipping d'une caméra.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "focal_length": {"type": "number"}, "near_clipping_plane": {"type": "number"}, "far_clipping_plane": {"type": "number"}}}}
    registry["set_camera_transform"] = {"handler": set_camera_transform, "main_thread": True, "description": "Anime la position et la rotation d’une vraie caméra de scène.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "position": {"type": "object"}, "rotation_degrees": {"type": "object"}}, "required": ["name"]}}
    registry["set_camera_focal_key"] = {"handler": set_camera_focal_key, "main_thread": True, "description": "Pose une clé de focale à la frame courante.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "focal_length": {"type": "number"}, "strength": {"type": "number"}}, "required": ["focal_length"]}}
    registry["set_camera_dof"] = {"handler": set_camera_dof, "main_thread": True, "description": "Pose une clé de profondeur de champ avec focus et portée.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "enabled": {"type": "boolean"}, "focus": {"type": "number"}, "range": {"type": "number"}, "strength": {"type": "number"}}, "required": []}}
    registry["set_current_camera"] = {"handler": set_current_camera, "main_thread": True, "description": "Active une caméra de scène pour le viewport et le rendu.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
    registry["set_camera_look_at"] = {"handler": set_camera_look_at, "main_thread": True, "description": "Oriente une caméra vers un objet à la frame courante en créant des clés de rotation.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "target_name": {"type": "string"}}, "required": ["target_name"]}}
