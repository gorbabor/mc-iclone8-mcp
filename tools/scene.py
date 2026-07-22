import RLPy
from tools.objects import find_by_name


_TYPES = {
    "object": RLPy.EObjectType_Object,
    "avatar": RLPy.EObjectType_Avatar,
    "prop": RLPy.EObjectType_Prop,
    "camera": RLPy.EObjectType_Camera,
    "light": RLPy.EObjectType_Light,
    "particle": RLPy.EObjectType_Particle,
}


def _object_summary(obj):
    transform = obj.LocalTransform()
    position = transform.T()
    return {"id": obj.GetID(), "name": obj.GetName(), "type": obj.GetType(), "position": {"x": position.x, "y": position.y, "z": position.z}}


def list_objects(args):
    object_type = args.get("type", "object").lower()
    if object_type not in _TYPES:
        raise ValueError("Unsupported object type: %s" % object_type)
    return {"objects": [_object_summary(obj) for obj in RLPy.RScene.FindObjects(_TYPES[object_type])]}


def get_selection(_args):
    return {"objects": [_object_summary(obj) for obj in RLPy.RScene.GetSelectedObjects()]}


def select_object(args):
    name = args["name"]
    obj = find_by_name(name)
    RLPy.RScene.SelectObject(obj)
    return {"status": "ok", "name": obj.GetName()}


def set_visibility(args):
    obj = find_by_name(args["name"])
    result = obj.SetVisible(RLPy.RGlobal.GetTime(), args["visible"])
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not change visibility")
    return {"status": "ok", "name": obj.GetName(), "visible": args["visible"]}


def delete_object(args):
    obj = find_by_name(args["name"])
    result = RLPy.RScene.RemoveObject(obj)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not remove object")
    return {"status": "ok", "name": args["name"]}


def register(registry):
    registry["list_objects"] = {"handler": list_objects, "main_thread": True, "description": "Liste les objets de la scène iClone 8.", "inputSchema": {"type": "object", "properties": {"type": {"type": "string", "enum": list(_TYPES)}}}}
    registry["get_selection"] = {"handler": get_selection, "main_thread": True, "description": "Retourne la sélection active dans iClone.", "inputSchema": {"type": "object", "properties": {}}}
    registry["select_object"] = {"handler": select_object, "main_thread": True, "description": "Sélectionne un objet de la scène par son nom.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
    registry["set_visibility"] = {"handler": set_visibility, "main_thread": True, "description": "Affiche ou masque un objet à l'instant courant.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "visible": {"type": "boolean"}}, "required": ["name", "visible"]}}
    registry["delete_object"] = {"handler": delete_object, "main_thread": True, "description": "Supprime définitivement un objet de la scène.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
