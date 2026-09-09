import queue
import threading
import time

import RLPy


_queue = queue.Queue()
_timer = None
_callback = None

# Drain as many queued jobs as possible per timer tick, bounded by this
# wall-clock budget so a large batch never freezes iClone's UI thread for long.
# Remaining jobs run on the next tick. At least one job always runs per tick.
_TICK_BUDGET_SECONDS = 0.020


class _Callback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)

    def Timeout(self):
        deadline = time.time() + _TICK_BUDGET_SECONDS
        while True:
            try:
                function, done, result = _queue.get_nowait()
            except queue.Empty:
                return
            try:
                result["value"] = function()
            except Exception as error:
                result["error"] = error
            finally:
                done.set()
            if time.time() >= deadline:
                return


def start():
    global _timer, _callback
    if _timer is not None:
        return
    _timer = RLPy.RPyTimer()
    _timer.SetInterval(50)
    _timer.SetSingleShot(False)
    _callback = _Callback()
    _timer.RegisterPyTimerCallback(_callback)
    _timer.Start()


def run(function, timeout=120):
    if _timer is None:
        return function()
    done = threading.Event()
    result = {}
    _queue.put((function, done, result))
    if not done.wait(timeout):
        raise TimeoutError("iClone operation timed out")
    if "error" in result:
        raise result["error"]
    return result.get("value")
