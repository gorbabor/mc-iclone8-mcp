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


def get_materials(args):
    obj = _find(args["name"])
    component, targets = _targets(obj)
    materials = []
    for index, (mesh_name, material_name) in enumerate(targets):
        color = component.GetDiffuseColor(mesh_name, material_name)
        materials.append({"index": index, "mesh": mesh_name, "name": material_name, "diffuse": {"r": color.R(), "g": color.G(), "b": color.B()}})
    return {"name": obj.GetName(), "materials": materials}


def set_material_color(args):
    obj = _find(args["name"])
    component, targets = _targets(obj)
    index = args.get("material_index", 0)
    if index < 0 or index >= len(targets):
        raise ValueError("Material index not found: %s" % index)
    color = args["color"]
    key = RLPy.RKey()
    key.SetTime(RLPy.RGlobal.GetTime())
    if hasattr(RLPy, "ETransitionType_Step"):
        key.SetTransitionType(RLPy.ETransitionType_Step)
    mesh_name, material_name = targets[index]
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


def register(registry):
    registry["get_materials"] = {"handler": get_materials, "main_thread": True, "description": "Liste les matériaux et leurs couleurs diffuses.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}
    registry["set_material_color"] = {"handler": set_material_color, "main_thread": True, "description": "Applique une couleur diffuse RGB (valeurs 0 à 1). Par défaut, masque la texture diffuse afin que la couleur soit visible.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "material_index": {"type": "integer"}, "color": {"type": "object", "properties": {"r": {"type": "number"}, "g": {"type": "number"}, "b": {"type": "number"}}}, "override_diffuse_texture": {"type": "boolean", "description": "Masquer la texture diffuse (défaut : true)"}}, "required": ["name", "color"]}}
