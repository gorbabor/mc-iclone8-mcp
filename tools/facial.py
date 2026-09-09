import os

import RLPy

from tools.avatar import _avatar
from tools.common import rl_string


def _face(args):
    avatar = _avatar(args.get("avatar_name"))
    component = avatar.GetFaceComponent()
    if component is None:
        raise RuntimeError("Avatar has no facial component")
    return avatar, component


def _viseme(args):
    avatar = _avatar(args.get("avatar_name"))
    component = avatar.GetVisemeComponent()
    if component is None:
        raise RuntimeError("Avatar has no viseme component")
    return avatar, component


def get_face_info(args):
    avatar, face = _face(args)
    raw_groups = list(face.GetExpressionGroups()) if hasattr(face, "GetExpressionGroups") else []
    groups = [rl_string(group) for group in raw_groups]
    expressions = {}
    for raw_group, group in zip(raw_groups, groups):
        expressions[group] = [rl_string(name) for name in face.GetExpressionNames(raw_group)]
    return {
        "avatar": avatar.GetName(),
        "clip_count": face.GetClipCount() if hasattr(face, "GetClipCount") else None,
        "expression_groups": groups,
        "expressions": expressions,
        "expression_set_uid": rl_string(face.GetExpressionSetUid()) if hasattr(face, "GetExpressionSetUid") else None,
        "auto_blink_name": rl_string(face.GetAutoBlinkName()) if hasattr(face, "GetAutoBlinkName") else None,
        "auto_blink_names": [rl_string(name) for name in face.GetAutoBlinkNames()] if hasattr(face, "GetAutoBlinkNames") else [],
        "strength": face.GetStrength() if hasattr(face, "GetStrength") else None,
    }


def set_auto_blink(args):
    avatar, face = _face(args)
    result = face.SetAutoBlinkName(args["name"])
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not set the avatar auto-blink mode")
    return {"status": "ok", "avatar": avatar.GetName(), "auto_blink_name": args["name"]}


def set_face_expressiveness(args):
    avatar, face = _face(args)
    weight = float(args["weight"])
    if weight < 0 or weight > 100:
        raise ValueError("weight must be between 0 and 100")
    result = face.AddExpressivenessKey(RLPy.RGlobal.GetTime(), weight)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not add the expressiveness key")
    return {"status": "ok", "avatar": avatar.GetName(), "weight": weight}


def add_expression_keys(args):
    avatar, face = _face(args)
    expressions = args["expressions"]
    strengths = [float(value) for value in args["strengths"]]
    if not isinstance(expressions, list) or not expressions:
        raise ValueError("expressions must be a non-empty list")
    if len(strengths) % len(expressions) != 0:
        raise ValueError("strengths length must be a multiple of expressions length")
    if any(value < 0 or value > 100 for value in strengths):
        raise ValueError("expression strengths must be between 0 and 100")
    interval = RLPy.RTime(int(args.get("interval_ms", 0)))
    try:
        face.BeginKeyEditing()
        result = face.AddExpressionKeys(RLPy.RGlobal.GetTime(), expressions, strengths, interval)
    finally:
        face.EndKeyEditing()
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not add expression keys")
    return {"status": "ok", "avatar": avatar.GetName(), "expressions": expressions, "strengths": strengths}


def get_viseme_info(args):
    avatar, viseme = _viseme(args)
    return {
        "avatar": avatar.GetName(),
        "clip_count": viseme.GetClipCount() if hasattr(viseme, "GetClipCount") else None,
        "viseme_names": [rl_string(name) for name in viseme.GetVisemeNames()] if hasattr(viseme, "GetVisemeNames") else [],
        "viseme_bones": [bone.GetName() for bone in viseme.GetVisemeBones()] if hasattr(viseme, "GetVisemeBones") else [],
        "viseme_morph_weights": list(viseme.GetVisemeMorphWeights()) if hasattr(viseme, "GetVisemeMorphWeights") else [],
        "strength": viseme.GetStrength() if hasattr(viseme, "GetStrength") else None,
    }


def add_viseme_key(args):
    avatar, viseme = _viseme(args)
    key = RLPy.RVisemeKey(int(args["viseme_id"]), float(args.get("expressiveness", 50)))
    key.SetTime(RLPy.RGlobal.GetTime())
    result = viseme.AddVisemeKey(key)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not add the viseme key")
    return {"status": "ok", "avatar": avatar.GetName(), "viseme_id": int(args["viseme_id"]), "expressiveness": float(args.get("expressiveness", 50))}


def load_vocal(args):
    avatar, viseme = _viseme(args)
    path = os.path.abspath(args["audio_path"])
    if not os.path.isfile(path):
        raise FileNotFoundError("Audio file not found: %s" % path)
    audio = RLPy.RAudio.CreateAudioObject()
    if audio.Load(path) != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not load the audio file")
    frame = int(args.get("start_frame", 0))
    time = RLPy.RGlobal.GetFps().IndexedFrameTime(frame)
    clip_name = args.get("clip_name", "MCP_Vocal")
    result = viseme.LoadVocal(audio, time, clip_name)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not create visemes from the audio")
    return {"status": "ok", "avatar": avatar.GetName(), "audio_path": path, "clip_name": clip_name, "start_frame": frame}


def register(registry):
    registry["get_face_info"] = {"handler": get_face_info, "main_thread": True, "description": "Inspect the facial expressions and settings available on an avatar.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}}}}
    registry["set_auto_blink"] = {"handler": set_auto_blink, "main_thread": True, "description": "Configure the auto-blink mode documented by iClone.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}, "name": {"type": "string"}}, "required": ["name"]}}
    registry["set_face_expressiveness"] = {"handler": set_face_expressiveness, "main_thread": True, "description": "Add a facial expressiveness key between 0 and 100.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}, "weight": {"type": "number", "minimum": 0, "maximum": 100}}, "required": ["weight"]}}
    registry["add_expression_keys"] = {"handler": add_expression_keys, "main_thread": True, "description": "Add facial expression keys with their intensities.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}, "expressions": {"type": "array", "items": {"type": "string"}}, "strengths": {"type": "array", "items": {"type": "number"}}, "interval_ms": {"type": "integer", "minimum": 0}}, "required": ["expressions", "strengths"]}}
    registry["get_viseme_info"] = {"handler": get_viseme_info, "main_thread": True, "description": "Inspect the visemes, clips and morph weights available on an avatar.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}}}}
    registry["add_viseme_key"] = {"handler": add_viseme_key, "main_thread": True, "description": "Add a viseme key at the current frame using the documented RLPy id.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}, "viseme_id": {"type": "integer"}, "expressiveness": {"type": "number", "minimum": 0, "maximum": 100}}, "required": ["viseme_id"]}}
    registry["load_vocal"] = {"handler": load_vocal, "main_thread": True, "description": "Load an audio file and create a viseme clip on an avatar.", "inputSchema": {"type": "object", "properties": {"avatar_name": {"type": "string"}, "audio_path": {"type": "string"}, "clip_name": {"type": "string"}, "start_frame": {"type": "integer", "minimum": 0}}, "required": ["audio_path"]}}
