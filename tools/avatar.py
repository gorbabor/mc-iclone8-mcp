import RLPy


def _avatar(name=None):
    if name:
        avatar = RLPy.RScene.FindObject(RLPy.EObjectType_Avatar, name)
        if avatar is None:
            raise ValueError("Avatar not found: %s" % name)
        return avatar
    avatars = RLPy.RScene.FindObjects(RLPy.EObjectType_Avatar)
    if not avatars:
        raise ValueError("No avatar in scene")
    return avatars[0]


def get_skin_bones(args):
    avatar = _avatar(args.get("avatar_name"))
    skeleton = avatar.GetSkeletonComponent()
    if skeleton is None:
        raise RuntimeError("Avatar has no skeleton component")
    bones = skeleton.GetSkinBones()
    return {
        "avatar": avatar.GetName(),
        "bone_count": len(bones),
        "bones": [{"name": bone.GetName()} for bone in bones],
    }


def get_avatar_info(args):
    """Give an agent a compact, non-destructive view of an avatar's capabilities."""
    avatar = _avatar(args.get("avatar_name"))
    skeleton = avatar.GetSkeletonComponent()
    clips = skeleton.GetClipCount() if skeleton is not None else 0
    bones = len(skeleton.GetSkinBones()) if skeleton is not None else 0
    return {
        "avatar": avatar.GetName(),
        "id": avatar.GetID(),
        "has_skeleton": skeleton is not None,
        "skin_bone_count": bones,
        "clip_count": clips,
        "mesh_count": len(avatar.GetMeshNames()),
    }


def get_avatar_capabilities(args):
    """Report which optional iClone 8 avatar components are available on an asset."""
    avatar = _avatar(args.get("avatar_name"))
    components = {
        "skeleton": "GetSkeletonComponent",
        "face": "GetFaceComponent",
        "viseme": "GetVisemeComponent",
        "morph": "GetMorphComponent",
        "material": "GetMaterialComponent",
        "hik_effector": "GetHikEffectorComponent",
        "physics": "GetPhysicsComponent",
    }
    available = {}
    for name, method_name in components.items():
        method = getattr(avatar, method_name, None)
        available[name] = bool(method and method() is not None)
    return {"avatar": avatar.GetName(), "components": available}


def get_animation_clips(args):
    avatar = _avatar(args.get("avatar_name"))
    skeleton = avatar.GetSkeletonComponent()
    if skeleton is None:
        raise RuntimeError("Avatar has no skeleton component")
    clips = []
    for index in range(skeleton.GetClipCount()):
        clip = skeleton.GetClip(index)
        clips.append({
            "index": index,
            "type": clip.GetType(),
            "speed": clip.GetSpeed(),
            "loop_count": clip.GetLoopCount(),
        })
    return {"avatar": avatar.GetName(), "clip_count": len(clips), "clips": clips}


def set_clip_speed(args):
    avatar = _avatar(args.get("avatar_name"))
    skeleton = avatar.GetSkeletonComponent()
    if skeleton is None:
        raise RuntimeError("Avatar has no skeleton component")
    index = args["clip_index"]
    if index < 0 or index >= skeleton.GetClipCount():
        raise ValueError("clip_index is outside the available clips")
    speed = float(args["speed"])
    if speed <= 0:
        raise ValueError("speed must be greater than zero")
    result = skeleton.GetClip(index).SetSpeed(speed)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set clip speed")
    return {"status": "ok", "avatar": avatar.GetName(), "clip_index": index, "speed": speed}


def set_clip_loop_count(args):
    avatar = _avatar(args.get("avatar_name"))
    skeleton = avatar.GetSkeletonComponent()
    if skeleton is None:
        raise RuntimeError("Avatar has no skeleton component")
    index = args["clip_index"]
    if index < 0 or index >= skeleton.GetClipCount():
        raise ValueError("clip_index is outside the available clips")
    loop_count = int(args["loop_count"])
    if loop_count < 0:
        raise ValueError("loop_count must be zero or greater")
    result = skeleton.GetClip(index).SetLoopCount(loop_count)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set clip loop count")
    return {"status": "ok", "avatar": avatar.GetName(), "clip_index": index, "loop_count": loop_count}


def register(registry):
    registry["get_avatar_info"] = {"handler": get_avatar_info, "main_thread": True, "description": "Retourne les informations essentielles d’un avatar : squelette, clips et meshes.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}}}}
    registry["get_avatar_capabilities"] = {"handler": get_avatar_capabilities, "main_thread": True, "description": "Indique les composants réellement disponibles sur l’avatar : squelette, face, visème, morph, matériau, HIK et physique.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}}}}
    registry["get_skin_bones"] = {"handler": get_skin_bones, "main_thread": True, "description": "Liste les os de skin d’un avatar iClone 8. Les anciens motion bones d’iClone 7 ne sont pas utilisés.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}}}}
    registry["get_animation_clips"] = {"handler": get_animation_clips, "main_thread": True, "description": "Liste les clips d’animation de l’avatar et leurs paramètres de lecture.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}}}}
    registry["set_clip_speed"] = {"handler": set_clip_speed, "main_thread": True, "description": "Change la vitesse d’un clip d’animation existant.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}, "clip_index": {"type": "integer", "minimum": 0}, "speed": {"type": "number", "exclusiveMinimum": 0}}, "required": ["clip_index", "speed"]}}
    registry["set_clip_loop_count"] = {"handler": set_clip_loop_count, "main_thread": True, "description": "Règle le nombre de boucles d’un clip d’animation existant (0 ou plus).", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}, "clip_index": {"type": "integer", "minimum": 0}, "loop_count": {"type": "integer", "minimum": 0}}, "required": ["clip_index", "loop_count"]}}
