import glob
import os
import select
import subprocess
from dataclasses import dataclass, field
from time import sleep

from evdev import InputDevice, ecodes


DEFAULT_DEVICE = "/dev/input/event5"
DEFAULT_CONTROLLER_MAC = "40:8E:2C:4A:2D:2E"
LEFT_STICK_X = ecodes.ABS_X
LEFT_STICK_Y = ecodes.ABS_Y


@dataclass
class ControllerState:
    x: float = 0
    y: float = 0
    buttons: list[str] = field(default_factory=list)
    changed: bool = False


def normalize_axis(value, absinfo):
    center = (absinfo.min + absinfo.max) / 2
    span = (absinfo.max - absinfo.min) / 2

    if span <= 0:
        return 0

    return max(-1, min(1, (value - center) / span))


def apply_deadzone(value, deadzone):
    if abs(value) < deadzone:
        return 0

    scaled = (abs(value) - deadzone) / (1 - deadzone)
    return scaled if value > 0 else -scaled


def find_device(path=DEFAULT_DEVICE):
    if os.path.exists(path) and is_drive_device(path):
        return path

    for candidate in sorted(glob.glob("/dev/input/event*")):
        if is_drive_device(candidate):
            return candidate

    return None


def is_drive_device(path):
    try:
        device = InputDevice(path)
        device.absinfo(LEFT_STICK_X)
        device.absinfo(LEFT_STICK_Y)
    except OSError:
        return False

    return "xbox" in device.name.lower()


def connect_controller(mac=DEFAULT_CONTROLLER_MAC):
    try:
        subprocess.run(
            ["bluetoothctl", "connect", mac],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"Bluetooth connect attempt failed: {error}", flush=True)


def connect_xbox_controller(
    device_path=DEFAULT_DEVICE,
    controller_mac=DEFAULT_CONTROLLER_MAC,
    deadzone=0.08,
):
    try:
        controller = XboxController(
            device_path=device_path,
            controller_mac=controller_mac,
            deadzone=deadzone,
            wait=False,
        )
    except (FileNotFoundError, OSError):
        connect_controller(controller_mac)
        raise

    print(f"Connected to {controller.name} at {controller.device_path}", flush=True)
    print("Left stick drives live. Release to center/stop.", flush=True)
    return controller


def wait_for_device(path=DEFAULT_DEVICE, controller_mac=DEFAULT_CONTROLLER_MAC):
    while True:
        device_path = find_device(path)

        if device_path:
            return device_path

        print(
            f"Waiting for Xbox controller {controller_mac}; trying Bluetooth connect",
            flush=True,
        )
        connect_controller(controller_mac)
        sleep(5)


class XboxController:
    """Xbox controller reader that owns connection and event polling."""

    def __init__(
        self,
        device_path=DEFAULT_DEVICE,
        controller_mac=DEFAULT_CONTROLLER_MAC,
        deadzone=0.08,
        wait=True,
    ):
        if not 0 <= deadzone < 1:
            raise ValueError("deadzone must be at least 0 and less than 1")

        self.device_path = (
            wait_for_device(device_path, controller_mac)
            if wait
            else find_device(device_path)
        )
        if not self.device_path:
            raise FileNotFoundError("Xbox controller drive device not found")

        self.device = InputDevice(self.device_path)
        self.deadzone = deadzone
        self.x_value = self.device.absinfo(LEFT_STICK_X).value
        self.y_value = self.device.absinfo(LEFT_STICK_Y).value
        self.state = self._state(changed=True)

    @property
    def name(self):
        return self.device.name

    def fileno(self):
        return self.device.fd

    def _state(self, buttons=None, changed=False):
        x_info = self.device.absinfo(LEFT_STICK_X)
        y_info = self.device.absinfo(LEFT_STICK_Y)
        x = apply_deadzone(normalize_axis(self.x_value, x_info), self.deadzone)
        y = apply_deadzone(-normalize_axis(self.y_value, y_info), self.deadzone)
        return ControllerState(x=x, y=y, buttons=buttons or [], changed=changed)

    def poll(self, timeout=0):
        readable, _, _ = select.select([self.device.fd], [], [], timeout)

        if not readable:
            self.state = self._state()
            return self.state

        changed = False
        buttons = []

        for event in self.device.read():
            if event.type == ecodes.EV_ABS:
                if event.code == LEFT_STICK_X:
                    self.x_value = event.value
                    changed = True
                elif event.code == LEFT_STICK_Y:
                    self.y_value = event.value
                    changed = True
            elif event.type == ecodes.EV_KEY and event.value:
                buttons.append(ecodes.KEY.get(event.code, str(event.code)))
                changed = True

        self.state = self._state(buttons=buttons, changed=changed)
        return self.state
