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

    def move(self, power):
        speed = min(1, abs(power))
        self.enable.value = speed

        if power > 0:
            self.motor.forward()
        elif power < 0:
            self.motor.backward()
        else:
            self.stop()

    def stop(self):
        self.motor.stop()
        self.enable.value = 0


def parse_args():
    parser = argparse.ArgumentParser(description="Pulse both rover sides with mixed drive power.")
    parser.add_argument("--left", type=float, default=0)
    parser.add_argument("--right", type=float, default=0)
    parser.add_argument("--seconds", type=float, default=0.5)
    return parser.parse_args()


args = parse_args()

if not -1 <= args.left <= 1:
    raise SystemExit("--left must be between -1 and 1")

if not -1 <= args.right <= 1:
    raise SystemExit("--right must be between -1 and 1")

if not 0 < args.seconds <= 5:
    raise SystemExit("--seconds must be greater than 0 and no more than 5")

left = Side(**{
    "forward_pin": PINS["left"]["forward"],
    "reverse_pin": PINS["left"]["reverse"],
    "enable_pin": PINS["left"]["enable"],
})
right = Side(**{
    "forward_pin": PINS["right"]["forward"],
    "reverse_pin": PINS["right"]["reverse"],
    "enable_pin": PINS["right"]["enable"],
})

try:
    print(
        f"mixed pulse left={args.left:+.0%} right={args.right:+.0%} "
        f"for {args.seconds:.2f}s"
    )
    left.move(args.left)
    right.move(args.right)
    sleep(args.seconds)
finally:
    left.stop()
    right.stop()
    print("stopped")
