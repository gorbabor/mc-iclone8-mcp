import RLPy

from tools.objects import find_by_name


def _find(name=None):
    camera = RLPy.RScene.FindObject(RLPy.EObjectType_Camera, name) if name else RLPy.RScene.GetCurrentCamera()
    if camera is None:
        raise ValueError("Camera not found")
    return camera


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
    control = camera.GetControl("Transform")
    if control is None:
        raise RuntimeError("Camera has no animable Transform control")
    block = control.GetDataBlock()
    time = RLPy.RGlobal.GetTime()
    for axis, value in zip(("X", "Y", "Z"), rotation):
        block.SetData("Rotation/Rotation" + axis, time, RLPy.RVariant(value))
    camera.Update()
    return {"status": "ok", "camera": camera.GetName(), "target": target.GetName()}


def register(registry):
    registry["get_camera"] = {"handler": get_camera, "main_thread": True, "description": "Lit les paramètres de la caméra active ou nommée.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}}}
    registry["set_camera"] = {"handler": set_camera, "main_thread": True, "description": "Modifie focale et plans de clipping d'une caméra.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "focal_length": {"type": "number"}, "near_clipping_plane": {"type": "number"}, "far_clipping_plane": {"type": "number"}}}}
    registry["set_current_camera"] = {"handler": set_current_camera, "main_thread": True, "description": "Active une caméra de scène pour le viewport et le rendu.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
    registry["set_camera_look_at"] = {"handler": set_camera_look_at, "main_thread": True, "description": "Oriente une caméra vers un objet à la frame courante en créant des clés de rotation.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "target_name": {"type": "string"}}, "required": ["target_name"]}}
