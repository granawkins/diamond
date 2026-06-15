from datetime import datetime
from pathlib import Path
from time import monotonic


CAPTURE_DIR = Path(__file__).resolve().parents[1] / "captures"


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def capture_path(prefix, extension):
    return CAPTURE_DIR / f"{prefix}_{timestamp()}.{extension.lstrip('.')}"


class OptionalController:
    """Retrying wrapper for hardware that may be disconnected at startup."""

    def __init__(self, name, connect, retry_interval=5):
        self.name = name
        self.connect = connect
        self.retry_interval = retry_interval
        self.device = None
        self.next_attempt = 0

    @property
    def available(self):
        return self.device is not None

    def tick(self, now=None):
        now = monotonic() if now is None else now

        if self.device is not None or now < self.next_attempt:
            return self.device

        self.next_attempt = now + self.retry_interval

        try:
            self.device = self.connect()
        except Exception as error:
            print(f"{self.name} unavailable: {error}", flush=True)
            self.device = None

        return self.device

    def clear(self, reason=None):
        if reason:
            print(f"{self.name} disconnected: {reason}", flush=True)
        self.device = None
        self.next_attempt = monotonic() + self.retry_interval
