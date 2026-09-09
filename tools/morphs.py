import RLPy

from tools.objects import find_by_name


def _target(args):
    if args.get("name"):
        obj = find_by_name(args["name"])
    else:
        selected = RLPy.RScene.GetSelectedObjects()
        if not selected:
            raise ValueError("name is required when no object is selected")
        obj = selected[0]
    if obj.GetType() not in (RLPy.EObjectType_Prop, RLPy.EObjectType_Avatar):
        raise ValueError("Morphs are only supported on props and avatars")
    component = obj.GetMorphComponent()
    if component is None:
        raise RuntimeError("Object has no morph component")
    return obj, component


def list_morphs(args):
    obj, component = _target(args)
    morphs = []
    for mesh in obj.GetMeshNames():
        for name in component.GetMorphNames(mesh):
            morphs.append({"mesh": mesh, "name": name})
    return {"object": obj.GetName(), "morph_count": len(morphs), "morphs": morphs}


def get_morph_weight(args):
    obj, component = _target(args)
    value = component.GetWeight(args["mesh"], args["morph"], RLPy.RGlobal.GetTime(), 0.0)
    weight = value[1] if isinstance(value, tuple) else value
    return {"object": obj.GetName(), "mesh": args["mesh"], "morph": args["morph"], "weight": weight}


def set_morph_weight(args):
    obj, component = _target(args)
    weight = float(args["weight"])
    result = component.AddKey(args["mesh"], args["morph"], RLPy.RGlobal.GetTime(), weight, False, False)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not add morph key")
    return {"status": "ok", "object": obj.GetName(), "mesh": args["mesh"], "morph": args["morph"], "weight": weight}


def register(registry):
    target = {"name": {"type": "string", "description": "Prop or avatar object (default: first selected object)."}}
    registry["list_morphs"] = {"handler": list_morphs, "main_thread": True, "description": "List available morphs, grouped by mesh.", "inputSchema": {"type": "object", "properties": target}}
    weight = dict(target)
    weight.update({"mesh": {"type": "string"}, "morph": {"type": "string"}})
    registry["get_morph_weight"] = {"handler": get_morph_weight, "main_thread": True, "description": "Read the morph weight at the current time.", "inputSchema": {"type": "object", "properties": weight, "required": ["mesh", "morph"]}}
    set_weight = dict(weight)
    set_weight["weight"] = {"type": "number"}
    registry["set_morph_weight"] = {"handler": set_morph_weight, "main_thread": True, "description": "Add a morph weight key at the current time.", "inputSchema": {"type": "object", "properties": set_weight, "required": ["mesh", "morph", "weight"]}}
