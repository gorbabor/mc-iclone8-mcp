import RLPy
from tools.objects import find_by_name
from tools.common import rl_string


_TYPES = {
    "object": RLPy.EObjectType_Object,
    "avatar": RLPy.EObjectType_Avatar,
    "prop": RLPy.EObjectType_Prop,
    "camera": RLPy.EObjectType_Camera,
    "light": RLPy.EObjectType_Light,
    "particle": RLPy.EObjectType_Particle,
}
if hasattr(RLPy, "EObjectType_Path"):
    _TYPES["path"] = RLPy.EObjectType_Path


def _object_summary(obj):
    transform = obj.LocalTransform()
    position = transform.T()
    return {"id": obj.GetID(), "name": obj.GetName(), "type": rl_string(obj.GetType()), "position": {"x": position.x, "y": position.y, "z": position.z}}


def list_objects(args):
    requested = args.get("type")
    if requested is None:
        # No type given: enumerate every known type, de-duplicated by object id
        # (subtype enums such as the light variants can overlap).
        seen = {}
        for enum in _TYPES.values():
            for obj in RLPy.RScene.FindObjects(enum):
                seen[obj.GetID()] = obj
        return {"objects": [_object_summary(obj) for obj in seen.values()]}
    object_type = requested.lower()
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
    if args.get("confirm") != "DELETE_OBJECT":
        raise ValueError("confirm must be DELETE_OBJECT")
    obj = find_by_name(args["name"])
    result = RLPy.RScene.RemoveObject(obj)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not remove object")
    return {"status": "ok", "name": args["name"]}


def clone_object(args):
    source = find_by_name(args["name"])
    clone = source.Clone()
    if clone is None:
        raise RuntimeError("iClone could not clone object")
    if args.get("new_name"):
        clone.SetName(args["new_name"])
    return _object_summary(clone)


def link_object(args):
    obj = find_by_name(args["name"])
    target = find_by_name(args["target_name"])
    alignments = {
        "none": "ELinkObjectAlignType_None",
        "position": "ELinkObjectAlignType_Position",
        "position_and_rotation": "ELinkObjectAlignType_Position_And_Rotation",
    }
    alignment = args.get("alignment", "position_and_rotation")
    if alignment not in alignments:
        raise ValueError("Unsupported alignment: %s" % alignment)
    result = obj.LinkTo(target, getattr(RLPy, alignments[alignment]), RLPy.RGlobal.GetTime())
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not link object")
    return {"status": "ok", "name": obj.GetName(), "target": target.GetName(), "alignment": alignment}


def unlink_object(args):
    obj = find_by_name(args["name"])
    result = obj.UnLink(RLPy.RGlobal.GetTime())
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not unlink object")
    return {"status": "ok", "name": obj.GetName()}


def align_object(args):
    obj = find_by_name(args["name"])
    target = find_by_name(args["target_name"])
    axes = {
        "x": "EAlignAxis_X_AXIS",
        "y": "EAlignAxis_Y_AXIS",
        "z": "EAlignAxis_Z_AXIS",
        "rotation": "EAlignAxis_ROTATE_AXIZ",
    }
    axis = args.get("axis", "rotation")
    if axis not in axes:
        raise ValueError("Unsupported alignment axis: %s" % axis)
    result = obj.AlignTo(target, getattr(RLPy, axes[axis]), args.get("to_pivot", True))
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not align object")
    return {"status": "ok", "name": obj.GetName(), "target": target.GetName(), "axis": axis}


def set_static(args):
    obj = find_by_name(args["name"])
    result = obj.SetStatic(args["static"])
    if result is not None and result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not change static state")
    return {"status": "ok", "name": obj.GetName(), "static": args["static"]}


def register(registry):
    registry["list_objects"] = {"handler": list_objects, "main_thread": True, "description": "Liste les objets de la scène iClone 8. Sans 'type', retourne tous les types.", "inputSchema": {"type": "object", "properties": {"type": {"type": "string", "enum": list(_TYPES)}}}}
    registry["get_selection"] = {"handler": get_selection, "main_thread": True, "description": "Retourne la sélection active dans iClone.", "inputSchema": {"type": "object", "properties": {}}}
    registry["select_object"] = {"handler": select_object, "main_thread": True, "description": "Sélectionne un objet de la scène par son nom.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
    registry["set_visibility"] = {"handler": set_visibility, "main_thread": True, "description": "Affiche ou masque un objet à l'instant courant.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "visible": {"type": "boolean"}}, "required": ["name", "visible"]}}
    registry["delete_object"] = {"handler": delete_object, "main_thread": True, "description": "Supprime définitivement un objet de la scène. Action destructive : confirm doit valoir DELETE_OBJECT.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "confirm": {"type": "string", "enum": ["DELETE_OBJECT"]}}, "required": ["name", "confirm"]}}
    registry["clone_object"] = {"handler": clone_object, "main_thread": True, "description": "Clone un objet de scène, avec un nouveau nom optionnel.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "new_name": {"type": "string"}}, "required": ["name"]}}
    registry["link_object"] = {"handler": link_object, "main_thread": True, "description": "Lie un objet à une cible à la frame courante.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "target_name": {"type": "string"}, "alignment": {"type": "string", "enum": ["none", "position", "position_and_rotation"]}}, "required": ["name", "target_name"]}}
    registry["unlink_object"] = {"handler": unlink_object, "main_thread": True, "description": "Dissocie un objet de sa cible à la frame courante.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
    registry["align_object"] = {"handler": align_object, "main_thread": True, "description": "Aligne un objet sur une cible selon un axe ou sa rotation.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "target_name": {"type": "string"}, "axis": {"type": "string", "enum": ["x", "y", "z", "rotation"]}, "to_pivot": {"type": "boolean"}}, "required": ["name", "target_name"]}}
    registry["set_static"] = {"handler": set_static, "main_thread": True, "description": "Active ou désactive le statut statique d’un objet.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "static": {"type": "boolean"}}, "required": ["name", "static"]}}
