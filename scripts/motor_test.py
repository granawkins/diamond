from time import sleep

from gpiozero import Motor, PWMOutputDevice


class Side:
    def __init__(self, forward_pin, reverse_pin, enable_pin):
        self.motor = Motor(forward=forward_pin, backward=reverse_pin)
        self.enable = PWMOutputDevice(enable_pin)

    def forward(self, speed=0.25):
        self.enable.value = speed
        self.motor.forward()

    def reverse(self, speed=0.25):
        self.enable.value = speed
        self.motor.backward()

    def stop(self):
        self.motor.stop()
        self.enable.value = 0


left = Side(forward_pin=5, reverse_pin=6, enable_pin=12)
right = Side(forward_pin=20, reverse_pin=21, enable_pin=13)


def pulse(label, action, duration=1):
    print(label)
    action()
    sleep(duration)
    left.stop()
    right.stop()
    sleep(1)


try:
    pulse("left forward", left.forward)
    pulse("left reverse", left.reverse)
    pulse("right forward", right.forward)
    pulse("right reverse", right.reverse)
    pulse("both forward", lambda: (left.forward(), right.forward()))
finally:
    left.stop()
    right.stop()
