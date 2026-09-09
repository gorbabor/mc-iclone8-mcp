import os
import math

import RLPy
from tools.common import current_time, require_success, require_unit_interval


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
    key.SetTime(current_time())
    if hasattr(RLPy, "ETransitionType_Step"):
        key.SetTransitionType(RLPy.ETransitionType_Step)
    return key


def get_materials(args):
    obj = _find(args["name"])
    component, targets = _targets(obj)
    materials = []
    for index, (mesh_name, material_name) in enumerate(targets):
        color = component.GetDiffuseColor(mesh_name, material_name)
        item = {"index": index, "mesh": mesh_name, "name": material_name, "diffuse": {"r": color.R(), "g": color.G(), "b": color.B()}}
        for label, method_name in (("ambient", "GetAmbientColor"), ("specular", "GetSpecularColor")):
            method = getattr(component, method_name, None)
            if method:
                try:
                    value = method(mesh_name, material_name)
                    item[label] = {"r": value.R(), "g": value.G(), "b": value.B()}
                except Exception:
                    item[label] = None
        for label, method_name in (("glossiness", "GetGlossinessWeight"), ("specular_weight", "GetSpecularWeight"), ("opacity", "GetOpacity"), ("self_illumination", "GetSelfIlluminationWeight")):
            method = getattr(component, method_name, None)
            if method:
                try:
                    item[label] = method(mesh_name, material_name)
                except Exception:
                    item[label] = None
        materials.append(item)
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
    value = require_unit_interval(value, "Material value")
    obj, component, index, mesh_name, material_name = _material_target(args)
    method = getattr(component, method_name, None)
    if method is None:
        raise RuntimeError("This iClone installation does not expose: %s" % method_name)
    result = method(_current_key(), mesh_name, material_name, value)
    require_success(result, "iClone could not apply material %s" % property_name)
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "property": property_name, "value": value}


def set_material_color_channel(args):
    obj, component, index, mesh_name, material_name = _material_target(args)
    channel = args.get("channel", "diffuse").lower()
    methods = {"ambient": "AddAmbientKey", "diffuse": "AddDiffuseKey", "specular": "AddSpecularKey"}
    method = getattr(component, methods.get(channel, ""), None)
    if method is None:
        raise ValueError("channel must be ambient, diffuse, or specular")
    color = args["color"]
    result = method(_current_key(), mesh_name, material_name, RLPy.RRgb(color.get("r", 1), color.get("g", 1), color.get("b", 1)))
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set material color channel")
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "channel": channel, "color": color}


def set_texture_weight(args):
    obj, component, index, mesh_name, material_name = _material_target(args)
    channel_name = args.get("channel", "diffuse").lower()
    enum_name = _TEXTURE_CHANNELS.get(channel_name)
    channel = getattr(RLPy, enum_name, None) if enum_name else None
    if channel is None:
        raise ValueError("Unsupported texture channel: %s" % channel_name)
    weight = float(args["weight"])
    weight = require_unit_interval(weight, "weight")
    result = component.AddTextureWeightKey(_current_key(), mesh_name, material_name, channel, weight)
    require_success(result, "iClone could not set texture weight")
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "channel": channel_name, "weight": weight}


def set_uv_data(args):
    obj, component, index, mesh_name, material_name = _material_target(args)
    channel_name = args.get("channel", "diffuse").lower()
    enum_name = _TEXTURE_CHANNELS.get(channel_name)
    channel = getattr(RLPy, enum_name, None) if enum_name else None
    if channel is None:
        raise ValueError("Unsupported texture channel: %s" % channel_name)
    offset, tile = args.get("offset", {}), args.get("tile", {})
    uv_offset = RLPy.RVector2(offset.get("x", 0), offset.get("y", 0))
    uv_tile = RLPy.RVector2(tile.get("x", 1), tile.get("y", 1))
    rotate = math.radians(float(args.get("rotate_degrees", 0)))
    result = component.AddUvDataKey(_current_key(), mesh_name, material_name, channel, uv_offset, uv_tile, rotate)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set UV data")
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "channel": channel_name, "offset": offset, "tile": tile, "rotate_degrees": float(args.get("rotate_degrees", 0))}


def load_video_texture(args):
    obj, component, index, mesh_name, material_name = _material_target(args)
    video_path = os.path.abspath(args["video_path"])
    if not os.path.isfile(video_path):
        raise FileNotFoundError("Video file not found: %s" % video_path)
    channel_name = args.get("channel", "diffuse").lower()
    enum_name = _TEXTURE_CHANNELS.get(channel_name)
    channel = getattr(RLPy, enum_name, None) if enum_name else None
    if channel is None:
        raise ValueError("Unsupported texture channel: %s" % channel_name)
    key = _current_key()
    result = component.LoadVideoToTexture(key, mesh_name, material_name, channel, video_path)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not load video texture")
    if "volume" in args and hasattr(component, "AddVideoVolumeKey"):
        volume = float(args["volume"])
        if component.AddVideoVolumeKey(key, mesh_name, material_name, channel, volume, bool(args.get("mute", False))) != RLPy.RStatus.Success:
            raise RuntimeError("iClone could not set video texture volume")
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "channel": channel_name, "video_path": video_path}


def set_material_attribute(args):
    obj, component, index, mesh_name, material_name = _material_target(args)
    method = getattr(component, "SetAttributeValue", None)
    if method is None:
        raise RuntimeError("This iClone installation does not expose SetAttributeValue")
    attribute = args["attribute"]
    if attribute not in ("TessellationLevel", "TessellationMultiplier", "TessellationThreshold"):
        raise ValueError("Unsupported attribute")
    result = method(mesh_name, material_name, attribute, float(args["value"]))
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set material attribute")
    return {"status": "ok", "name": obj.GetName(), "material_index": index, "attribute": attribute, "value": float(args["value"])}


def register(registry):
    registry["get_materials"] = {"handler": get_materials, "main_thread": True, "description": "List materials and their diffuse colors.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
    registry["set_material_color"] = {"handler": set_material_color, "main_thread": True, "description": "Apply an RGB diffuse color (values 0 to 1). By default hides the diffuse texture so the color is visible.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "color": {"type": "object", "properties": {"r": {"type": "number"}, "g": {"type": "number"}, "b": {"type": "number"}}}, "override_diffuse_texture": {"type": "boolean", "description": "Hide the diffuse texture (default: true)"}}, "required": ["name", "color"]}}
    registry["set_material_texture"] = {"handler": set_material_texture, "main_thread": True, "description": "Load a local image into an iClone material channel (diffuse, metallic, specular, glow, opacity, bump, reflection or ambient_occlusion).", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "channel": {"type": "string"}, "texture_path": {"type": "string"}}, "required": ["name", "texture_path"]}}
    registry["set_material_value"] = {"handler": set_material_value, "main_thread": True, "description": "Set an animatable material value at the current time: opacity, glossiness or self_illumination (0 to 1).", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "property": {"type": "string"}, "value": {"type": "number", "minimum": 0, "maximum": 1}}, "required": ["name", "property", "value"]}}
    registry["set_material_color_channel"] = {"handler": set_material_color_channel, "main_thread": True, "description": "Set an ambient, diffuse or specular color.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "channel": {"type": "string", "enum": ["ambient", "diffuse", "specular"]}, "color": {"type": "object"}}, "required": ["name", "channel", "color"]}}
    registry["set_texture_weight"] = {"handler": set_texture_weight, "main_thread": True, "description": "Set a material texture's weight between 0 and 1.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "channel": {"type": "string"}, "weight": {"type": "number", "minimum": 0, "maximum": 1}}, "required": ["name", "weight"]}}
    registry["set_uv_data"] = {"handler": set_uv_data, "main_thread": True, "description": "Animate a texture channel's UV offset, tiling and rotation.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "channel": {"type": "string"}, "offset": {"type": "object"}, "tile": {"type": "object"}, "rotate_degrees": {"type": "number"}}, "required": ["name"]}}
    registry["load_video_texture"] = {"handler": load_video_texture, "main_thread": True, "description": "Load a video into a texture channel and optionally set its volume.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "channel": {"type": "string"}, "video_path": {"type": "string"}, "volume": {"type": "number"}, "mute": {"type": "boolean"}}, "required": ["name", "video_path"]}}
    registry["set_material_attribute"] = {"handler": set_material_attribute, "main_thread": True, "description": "Set a tessellation attribute documented by RIMaterialComponent.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "attribute": {"type": "string", "enum": ["TessellationLevel", "TessellationMultiplier", "TessellationThreshold"]}, "value": {"type": "number"}}, "required": ["name", "attribute", "value"]}}
