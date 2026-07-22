import RLPy


def _find(name):
    light = RLPy.RScene.FindObject(RLPy.EObjectType_Light, name) if name else None
    if light is None:
        lights = RLPy.RScene.FindObjects(RLPy.EObjectType_Light)
        if not lights:
            raise ValueError("No light found")
        light = lights[0]
    return light


def get_light(args):
    light = _find(args.get("name"))
    color = light.GetColor()
    return {"name": light.GetName(), "active": light.GetActive(), "multiplier": light.GetMultiplier(), "color": {"r": color.R(), "g": color.G(), "b": color.B()}}


def set_light(args):
    light = _find(args.get("name"))
    time = RLPy.RGlobal.GetTime()
    if "active" in args:
        try:
            result = light.SetActive(time, args["active"])
        except TypeError:
            result = light.SetActive(args["active"])
        if result != RLPy.RStatus.Success:
            raise RuntimeError("iClone could not change light state")
    if "multiplier" in args and light.SetMultiplier(time, args["multiplier"]) != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not change light multiplier")
    if "color" in args:
        value = args["color"]
        if light.SetColor(time, RLPy.RRgb(value.get("r", 1), value.get("g", 1), value.get("b", 1))) != RLPy.RStatus.Success:
            raise RuntimeError("iClone could not change light color")
    return get_light({"name": light.GetName()})


def register(registry):
    registry["get_light"] = {"handler": get_light, "main_thread": True, "description": "Lit l'état, l'intensité et la couleur d'une lumière.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}}}
    registry["set_light"] = {"handler": set_light, "main_thread": True, "description": "Modifie l'état, l'intensité ou la couleur d'une lumière.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "active": {"type": "boolean"}, "multiplier": {"type": "number"}, "color": {"type": "object"}}}}
