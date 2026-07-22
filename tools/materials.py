import os

import RLPy


def _find(name):
    obj = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, name)
    if obj is None:
        obj = RLPy.RScene.FindObject(RLPy.EObjectType_Avatar, name)
    if obj is None:
        raise ValueError("Object not found: %s" % name)
    return obj


def _targets(obj):
    component = obj.GetMaterialComponent()
    targets = []
    for mesh_name in obj.GetMeshNames():
        for material_name in component.GetMaterialNames(mesh_name):
            targets.append((mesh_name, material_name))
    return component, targets


def _material_target(args):
    obj = _find(args["name"])
    component, targets = _targets(obj)
    index = args.get("material_index", 0)
    if index < 0 or index >= len(targets):
        raise ValueError("Material index not found: %s" % index)
    mesh_name, material_name = targets[index]
    return obj, component, index, mesh_name, material_name


def _current_key():
    key = RLPy.RKey()
    key.SetTime(RLPy.RGlobal.GetTime())
    if hasattr(RLPy, "ETransitionType_Step"):
        key.SetTransitionType(RLPy.ETransitionType_Step)
    return key


def get_materials(args):
    obj = _find(args["name"])
    component, targets = _targets(obj)
    materials = []
    for index, (mesh_name, material_name) in enumerate(targets):
        color = component.GetDiffuseColor(mesh_name, material_name)
        materials.append({"index": index, "mesh": mesh_name, "name": material_name, "diffuse": {"r": color.R(), "g": color.G(), "b": color.B()}})
    return {"name": obj.GetName(), "materials": materials}


def set_material_color(args):
    obj, component, index, mesh_name, material_name = _material_target(args)
    color = args["color"]
    key = _current_key()
    rgb = RLPy.RRgb(color.get("r", 1.0), color.get("g", 1.0), color.get("b", 1.0))
    override_texture = args.get("override_diffuse_texture", True)
    if override_texture:
        result = component.AddTextureWeightKey(
            key, mesh_name, material_name, RLPy.EMaterialTextureChannel_Diffuse, 0.0
        )
        if result != RLPy.RStatus.Success:
            raise RuntimeError("iClone could not reduce diffuse texture contribution")
    result = component.AddDiffuseKey(key, mesh_name, material_name, rgb)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not apply diffuse color")
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "color": color, "override_diffuse_texture": override_texture}


_TEXTURE_CHANNELS = {
    "diffuse": "EMaterialTextureChannel_Diffuse",
    "metallic": "EMaterialTextureChannel_Metallic",
    "specular": "EMaterialTextureChannel_Specular",
    "glow": "EMaterialTextureChannel_Glow",
    "opacity": "EMaterialTextureChannel_Opacity",
    "bump": "EMaterialTextureChannel_Bump",
    "reflection": "EMaterialTextureChannel_Reflection",
    "ambient_occlusion": "EMaterialTextureChannel_AmbientOcclusion",
}


def set_material_texture(args):
    """Load an image into one of the documented iClone material channels."""
    texture_path = os.path.abspath(args["texture_path"])
    if not os.path.isfile(texture_path):
        raise ValueError("Texture file not found: %s" % texture_path)
    channel_name = args.get("channel", "diffuse").lower()
    enum_name = _TEXTURE_CHANNELS.get(channel_name)
    if enum_name is None:
        raise ValueError("Unsupported channel. Use one of: %s" % ", ".join(sorted(_TEXTURE_CHANNELS)))
    channel = getattr(RLPy, enum_name, None)
    if channel is None:
        raise RuntimeError("This iClone installation does not expose material channel: %s" % channel_name)
    obj, component, index, mesh_name, material_name = _material_target(args)
    result = component.LoadImageToTexture(mesh_name, material_name, channel, texture_path)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not load the texture into the %s channel" % channel_name)
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "channel": channel_name, "texture_path": texture_path}


_MATERIAL_VALUE_METHODS = {
    "opacity": "AddOpacityKey",
    "glossiness": "AddGlossinessKey",
    "self_illumination": "AddSelfIlluminationKey",
}


def set_material_value(args):
    """Set an animatable scalar material property at the current timeline frame."""
    property_name = args["property"].lower()
    method_name = _MATERIAL_VALUE_METHODS.get(property_name)
    if method_name is None:
        raise ValueError("Unsupported property. Use one of: %s" % ", ".join(sorted(_MATERIAL_VALUE_METHODS)))
    value = float(args["value"])
    if value < 0.0 or value > 1.0:
        raise ValueError("Material value must be between 0 and 1")
    obj, component, index, mesh_name, material_name = _material_target(args)
    method = getattr(component, method_name, None)
    if method is None:
        raise RuntimeError("This iClone installation does not expose: %s" % method_name)
    result = method(_current_key(), mesh_name, material_name, value)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not apply material %s" % property_name)
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "property": property_name, "value": value}


def register(registry):
    registry["get_materials"] = {"handler": get_materials, "main_thread": True, "description": "Liste les matériaux et leurs couleurs diffuses.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
    registry["set_material_color"] = {"handler": set_material_color, "main_thread": True, "description": "Applique une couleur diffuse RGB (valeurs 0 à 1). Par défaut, masque la texture diffuse afin que la couleur soit visible.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "color": {"type": "object", "properties": {"r": {"type": "number"}, "g": {"type": "number"}, "b": {"type": "number"}}}, "override_diffuse_texture": {"type": "boolean", "description": "Masquer la texture diffuse (défaut : true)"}}, "required": ["name", "color"]}}
    registry["set_material_texture"] = {"handler": set_material_texture, "main_thread": True, "description": "Charge une image locale dans un canal de matériau iClone (diffuse, metallic, specular, glow, opacity, bump, reflection ou ambient_occlusion).", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "channel": {"type": "string"}, "texture_path": {"type": "string"}}, "required": ["name", "texture_path"]}}
    registry["set_material_value"] = {"handler": set_material_value, "main_thread": True, "description": "Règle une valeur de matériau animable au temps courant : opacity, glossiness ou self_illumination (0 à 1).", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "property": {"type": "string"}, "value": {"type": "number", "minimum": 0, "maximum": 1}}, "required": ["name", "property", "value"]}}
