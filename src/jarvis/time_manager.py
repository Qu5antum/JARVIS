import threading
import time

from src.tts.tts import speak


class TimerManager:
    def __init__(self):
        self.timers = {}
        self.lock = threading.Lock()

    def create(self, name: str, seconds: int):
        self.cancel(name)

        stop_event = threading.Event()

        timer = {
            "duration": seconds,
            "end_time": time.time() + seconds,
            "stop_event": stop_event,
        }

        with self.lock:
            self.timers[name] = timer

        thread = threading.Thread(
            target=self._run,
            args=(name, timer),
            daemon=True
        )

        thread.start()

    def _run(self, name, timer):
        stopped = timer["stop_event"].wait(timer["duration"])

        if stopped:
            return

        with self.lock:
            if name in self.timers:
                del self.timers[name]

        speak(f"Таймер {name} завершён")

    def cancel(self, name: str) -> bool:
        with self.lock:
            timer = self.timers.get(name)

            if not timer:
                return False

            timer["stop_event"].set()
            del self.timers[name]

        return True

    def remaining(self, name: str):
        with self.lock:
            timer = self.timers.get(name)

            if not timer:
                return None

            remaining = timer["end_time"] - time.time()

        return max(0, int(remaining))

    def exists(self, name: str):
        with self.lock:
            return name in self.timers