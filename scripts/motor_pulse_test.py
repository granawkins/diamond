import argparse
from time import sleep

from gpiozero import Motor, PWMOutputDevice


PINS = {
    "left": {"forward": 5, "reverse": 6, "enable": 12},
    "right": {"forward": 20, "reverse": 21, "enable": 13},
}


class Side:
    def __init__(self, forward_pin, reverse_pin, enable_pin):
        self.motor = Motor(forward=forward_pin, backward=reverse_pin)
        self.enable = PWMOutputDevice(enable_pin)

    def move(self, direction, speed):
        self.enable.value = speed
        if direction == "forward":
            self.motor.forward()
        else:
            self.motor.backward()

    def stop(self):
        self.motor.stop()
        self.enable.value = 0


def parse_args():
    parser = argparse.ArgumentParser(description="Pulse one rover side briefly.")
    parser.add_argument("--side", choices=["left", "right"], default="left")
    parser.add_argument("--direction", choices=["forward", "reverse"], default="forward")
    parser.add_argument("--speed", type=float, default=0.20)
    parser.add_argument("--seconds", type=float, default=0.5)
    return parser.parse_args()


args = parse_args()
pins = PINS[args.side]
side = Side(
    forward_pin=pins["forward"],
    reverse_pin=pins["reverse"],
    enable_pin=pins["enable"],
)

try:
    print(
        f"pulsing {args.side} {args.direction} "
        f"at {args.speed:.0%} for {args.seconds:.2f}s"
    )
    side.move(args.direction, args.speed)
    sleep(args.seconds)
finally:
    side.stop()
    print("stopped")
