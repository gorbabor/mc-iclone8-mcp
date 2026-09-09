import os

import RLPy

from tools.objects import _SEARCH_TYPES, find_by_name
from tools.common import current_time, require_success, rl_string


def _find(name):
    if name:
        for object_type in (RLPy.EObjectType_Light, RLPy.EObjectType_SpotLight, RLPy.EObjectType_PointLight, RLPy.EObjectType_DirectionalLight):
            light = RLPy.RScene.FindObject(object_type, name)
            if light is not None:
                return light
        raise ValueError("Light not found: %s" % name)
    for object_type in (RLPy.EObjectType_Light, RLPy.EObjectType_SpotLight, RLPy.EObjectType_PointLight, RLPy.EObjectType_DirectionalLight):
        lights = RLPy.RScene.FindObjects(object_type)
        if lights:
            return lights[0]
    raise ValueError("No light found")


def get_light(args):
    light = _find(args.get("name"))
    color = light.GetColor()
    data = {"name": light.GetName(), "type": rl_string(light.GetType()), "active": light.GetActive(), "multiplier": light.GetMultiplier(), "color": {"r": color.R(), "g": color.G(), "b": color.B()}}
    for key, method_name in (("range", "GetRange"), ("inverse_square", "GetInverseSquare"), ("cast_shadow", "IsCastShadow"), ("rectangle_shape", "IsRectangleShape"), ("tube_shape", "IsTubeShape"), ("tube_length", "GetTubeLength"), ("tube_radius", "GetTubeRadius"), ("tube_soft_radius", "GetTubeSoftRadius"), ("transmission", "GetTransmission"), ("shadow_strength", "GetDarkenShadowStrength")):
        method = getattr(light, method_name, None)
        if method:
            try:
                data[key] = method()
            except Exception:
                data[key] = None
    return data


def set_light(args):
    light = _find(args.get("name"))
    time = current_time()
    if "active" in args:
        try:
            result = light.SetActive(time, args["active"])
        except TypeError:
            result = light.SetActive(args["active"])
        require_success(result, "iClone could not change light state")
    if "multiplier" in args:
        require_success(light.SetMultiplier(time, args["multiplier"]), "iClone could not change light multiplier")
    if "color" in args:
        value = args["color"]
        require_success(light.SetColor(time, RLPy.RRgb(value.get("r", 1), value.get("g", 1), value.get("b", 1))), "iClone could not change light color")
    for key, method_name in (("range", "SetRange"), ("shadow_strength", "SetDarkenShadowStrength")):
        if key in args:
            method = getattr(light, method_name, None)
            if method is None:
                raise RuntimeError("This iClone installation does not expose light setting: %s" % key)
            require_success(method(time, float(args[key])), "iClone could not set light %s" % key)
    for key, method_name in (("inverse_square", "SetInverseSquare"), ("cast_shadow", "SetCastShadow"), ("rectangle_shape", "SetRectangleShape"), ("tube_shape", "SetTubeShape"), ("transmission", "SetTransmission")):
        if key in args:
            method = getattr(light, method_name, None)
            if method is None:
                raise RuntimeError("This iClone installation does not expose light setting: %s" % key)
            require_success(method(bool(args[key])), "iClone could not set light %s" % key)
    for key, method_name in (("tube_length", "SetTubeLength"), ("tube_radius", "SetTubeRadius"), ("tube_soft_radius", "SetTubeSoftRadius")):
        if key in args:
            method = getattr(light, method_name, None)
            if method is None:
                raise RuntimeError("This iClone installation does not expose light setting: %s" % key)
            require_success(method(float(args[key])), "iClone could not set light %s" % key)
    if "rect_width" in args or "rect_height" in args:
        method = getattr(light, "SetRectWidthHeight", None)
        if method is None or method(RLPy.RVector2(float(args.get("rect_width", 1)), float(args.get("rect_height", 1)))) != RLPy.RStatus.Success:
            raise RuntimeError("iClone could not set rectangular light dimensions")
    if any(key in args for key in ("spot_angle", "spot_falloff", "spot_attenuation")):
        method = getattr(light, "SetSpotLightBeam", None)
        if method is None or method(time, float(args.get("spot_angle", 45)), float(args.get("spot_falloff", 0)), float(args.get("spot_attenuation", 0))) != RLPy.RStatus.Success:
            raise RuntimeError("iClone could not set spotlight beam")
    for key, method_name in (("ies_path", "LoadIes"), ("rect_texture_path", "LoadRectTexture")):
        if key in args:
            path = os.path.abspath(args[key])
            if not os.path.isfile(path):
                raise FileNotFoundError("Light file not found: %s" % path)
            method = getattr(light, method_name, None)
            if method is None or method(path) != RLPy.RStatus.Success:
                raise RuntimeError("iClone could not load light file")
    if args.get("clear_rect_texture"):
        method = getattr(light, "ClearRectTexture", None)
        if method is None or method() != RLPy.RStatus.Success:
            raise RuntimeError("iClone could not clear rectangular light texture")
    return get_light({"name": light.GetName()})


def register(registry):
    registry["get_light"] = {"handler": get_light, "main_thread": True, "description": "Read an iClone 8 light's basic and advanced properties.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}}}
    registry["set_light"] = {"handler": set_light, "main_thread": True, "description": "Change iClone 8 lights' basic and advanced properties.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "active": {"type": "boolean"}, "multiplier": {"type": "number"}, "color": {"type": "object"}, "range": {"type": "number"}, "inverse_square": {"type": "boolean"}, "cast_shadow": {"type": "boolean"}, "rectangle_shape": {"type": "boolean"}, "tube_shape": {"type": "boolean"}, "tube_length": {"type": "number"}, "tube_radius": {"type": "number"}, "tube_soft_radius": {"type": "number"}, "rect_width": {"type": "number"}, "rect_height": {"type": "number"}, "spot_angle": {"type": "number"}, "spot_falloff": {"type": "number"}, "spot_attenuation": {"type": "number"}, "transmission": {"type": "boolean"}, "shadow_strength": {"type": "number"}, "ies_path": {"type": "string"}, "rect_texture_path": {"type": "string"}, "clear_rect_texture": {"type": "boolean"}}}}
