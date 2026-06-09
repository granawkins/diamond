import argparse
import glob
import os
import select
from time import sleep

from evdev import InputDevice, ecodes
from gpiozero import Motor, PWMOutputDevice


PINS = {
    "left": {"forward": 5, "reverse": 6, "enable": 12},
    "right": {"forward": 20, "reverse": 21, "enable": 13},
}

LEFT_STICK_X = ecodes.ABS_X
LEFT_STICK_Y = ecodes.ABS_Y


class Side:
    def __init__(self, forward_pin, reverse_pin, enable_pin):
        self.motor = Motor(forward=forward_pin, backward=reverse_pin)
        self.enable = PWMOutputDevice(enable_pin)
        self.power = None

    def move(self, power):
        power = max(-1, min(1, power))

        if self.power is not None and abs(power - self.power) < 0.01:
            return

        self.power = power
        self.enable.value = abs(power)

        if power > 0:
            self.motor.forward()
        elif power < 0:
            self.motor.backward()
        else:
            self.motor.stop()

    def stop(self):
        self.power = 0
        self.motor.stop()
        self.enable.value = 0


class RoverDrive:
    def __init__(self, max_speed):
        self.left = Side(
            forward_pin=PINS["left"]["forward"],
            reverse_pin=PINS["left"]["reverse"],
            enable_pin=PINS["left"]["enable"],
        )
        self.right = Side(
            forward_pin=PINS["right"]["forward"],
            reverse_pin=PINS["right"]["reverse"],
            enable_pin=PINS["right"]["enable"],
        )
        self.max_speed = max_speed

    def drive(self, throttle, steering):
        raw_left = throttle + steering
        raw_right = throttle - steering
        scale = max(1, abs(raw_left), abs(raw_right))

        left_power = (raw_left / scale) * self.max_speed
        right_power = (raw_right / scale) * self.max_speed

        self.left.move(left_power)
        self.right.move(right_power)
        print(
            f"throttle={throttle:+.0%} steering={steering:+.0%} "
            f"left={left_power:+.0%} right={right_power:+.0%}",
            flush=True,
        )

    def stop(self):
        self.left.stop()
        self.right.stop()


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


def mix_from_stick(device, x_value, y_value, deadzone):
    x_info = device.absinfo(LEFT_STICK_X)
    y_info = device.absinfo(LEFT_STICK_Y)

    steering = apply_deadzone(normalize_axis(x_value, x_info), deadzone)
    throttle = apply_deadzone(-normalize_axis(y_value, y_info), deadzone)

    return throttle, steering


def parse_args():
    parser = argparse.ArgumentParser(description="Drive the rover live from an Xbox left stick.")
    parser.add_argument("--device", default="/dev/input/event5")
    parser.add_argument("--deadzone", type=float, default=0.08)
    parser.add_argument("--max-speed", type=float, default=0.40)
    return parser.parse_args()


def find_device(path):
    if os.path.exists(path):
        return path

    for candidate in sorted(glob.glob("/dev/input/event*")):
        try:
            device = InputDevice(candidate)
        except OSError:
            continue

        if "xbox" in device.name.lower():
            return candidate

    return path


def main():
    args = parse_args()

    if not 0 <= args.deadzone < 1:
        raise SystemExit("--deadzone must be at least 0 and less than 1")

    if not 0 <= args.max_speed <= 1:
        raise SystemExit("--max-speed must be between 0 and 1")

    device_path = find_device(args.device)
    device = InputDevice(device_path)
    drive = RoverDrive(max_speed=args.max_speed)
    x_value = device.absinfo(LEFT_STICK_X).value
    y_value = device.absinfo(LEFT_STICK_Y).value

    print(f"Connected to {device.name} at {device_path}")
    print("Left stick drives live. Release to center/stop. Press Ctrl+C to exit.")

    try:
        throttle, steering = mix_from_stick(device, x_value, y_value, args.deadzone)
        drive.drive(throttle, steering)

        while True:
            readable, _, _ = select.select([device.fd], [], [], 0.25)

            if not readable:
                continue

            for event in device.read():
                if event.type != ecodes.EV_ABS:
                    continue

                if event.code == LEFT_STICK_X:
                    x_value = event.value
                elif event.code == LEFT_STICK_Y:
                    y_value = event.value
                else:
                    continue

                throttle, steering = mix_from_stick(device, x_value, y_value, args.deadzone)
                drive.drive(throttle, steering)

    except KeyboardInterrupt:
        print("Stopping")
    except OSError as error:
        print(f"Controller disconnected or unreadable: {error}")
    finally:
        drive.stop()
        sleep(0.05)


if __name__ == "__main__":
    main()
