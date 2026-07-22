import RLPy


def _frame(time, fps):
    return fps.GetFrameIndex(time)


def _time(frame, fps):
    return fps.IndexedFrameTime(frame)


def _fps_value(fps):
    return fps.ToFloat()


def get_timeline(_args):
    fps = RLPy.RGlobal.GetFps()
    current, start, end = RLPy.RGlobal.GetTime(), RLPy.RGlobal.GetStartTime(), RLPy.RGlobal.GetEndTime()
    return {
        "fps": _fps_value(fps),
        "playing": RLPy.RGlobal.IsPlaying(),
        "current_frame": _frame(current, fps),
        "start_frame": _frame(start, fps),
        "end_frame": _frame(end, fps),
    }


def set_timeline(args):
    if "frame" in args:
        target = _time(args["frame"], RLPy.RGlobal.GetFps())
    elif "milliseconds" in args:
        target = RLPy.RTime(args["milliseconds"])
    else:
        raise ValueError("frame or milliseconds is required")
    result = RLPy.RGlobal.SetTime(target)
    if result != RLPy.RStatus.Success:
        raise RuntimeError("iClone could not change timeline position")
    return get_timeline({})


def play(args):
    fps = RLPy.RGlobal.GetFps()
    start = _time(args.get("start_frame", _frame(RLPy.RGlobal.GetStartTime(), fps)), fps)
    end = _time(args.get("end_frame", _frame(RLPy.RGlobal.GetEndTime(), fps)), fps)
    RLPy.RGlobal.Play(start, end)
    return {"status": "ok"}


def pause(_args):
    RLPy.RGlobal.Pause()
    return get_timeline({})


def stop(_args):
    RLPy.RGlobal.Stop()
    return get_timeline({})


def register(registry):
    registry["get_timeline"] = {"handler": get_timeline, "main_thread": True, "description": "Retourne FPS, lecture et bornes de la timeline.", "inputSchema": {"type": "object", "properties": {}}}
    registry["set_timeline"] = {"handler": set_timeline, "main_thread": True, "description": "Place la tête de lecture par frame ou millisecondes.", "inputSchema": {"type": "object", "properties": {"frame": {"type": "integer"}, "milliseconds": {"type": "integer"}}}}
    registry["play_timeline"] = {"handler": play, "main_thread": True, "description": "Lance la lecture de la timeline.", "inputSchema": {"type": "object", "properties": {"start_frame": {"type": "integer"}, "end_frame": {"type": "integer"}}}}
    registry["pause_timeline"] = {"handler": pause, "main_thread": True, "description": "Met la timeline en pause.", "inputSchema": {"type": "object", "properties": {}}}
    registry["stop_timeline"] = {"handler": stop, "main_thread": True, "description": "Arrête la timeline.", "inputSchema": {"type": "object", "properties": {}}}
