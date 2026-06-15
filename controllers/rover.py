PINS = {
    "left": {"forward": 5, "reverse": 6, "enable": 12},
    "right": {"forward": 20, "reverse": 16, "enable": 13},
}


def clamp(value, minimum=-1, maximum=1):
    return max(minimum, min(maximum, value))


def validate_power(value, name="power"):
    power = float(value)
    if not -1 <= power <= 1:
        raise ValueError(f"{name} must be between -1 and 1")
    return power


def validate_speed(value, name="speed"):
    speed = float(value)
    if not 0 <= speed <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return speed


def mix_differential(y, x, max_speed=1):
    max_speed = validate_speed(max_speed, "max_speed")
    raw_left = float(y) + float(x)
    raw_right = float(y) - float(x)
    scale = max(1, abs(raw_left), abs(raw_right))

    return (
        clamp((raw_left / scale) * max_speed),
        clamp((raw_right / scale) * max_speed),
    )


class MotorSide:
    def __init__(self, forward_pin, reverse_pin, enable_pin):
        from gpiozero import Motor, PWMOutputDevice

        self.motor = Motor(forward=forward_pin, backward=reverse_pin)
        self.enable = PWMOutputDevice(enable_pin)
        self.power = None

    def move(self, power):
        power = clamp(float(power))

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


class Rover:
    """Skid-steer rover controller."""

    available = True

    def __init__(self, pins=PINS, max_speed=1):
        self.max_speed = validate_speed(max_speed, "max_speed")
        self.left = MotorSide(
            forward_pin=pins["left"]["forward"],
            reverse_pin=pins["left"]["reverse"],
            enable_pin=pins["left"]["enable"],
        )
        self.right = MotorSide(
            forward_pin=pins["right"]["forward"],
            reverse_pin=pins["right"]["reverse"],
            enable_pin=pins["right"]["enable"],
        )

    def drive(self, x, y):
        left_power, right_power = mix_differential(y, x, max_speed=self.max_speed)
        self.move(left_power, right_power)
        return {"left": left_power, "right": right_power}

    def move(self, left_power, right_power):
        self.left.move(validate_power(left_power, "left"))
        self.right.move(validate_power(right_power, "right"))

    def stop(self):
        self.left.stop()
        self.right.stop()


def connect_rover(max_speed=1, pins=PINS):
    """Create a real rover controller or raise if GPIO setup is unavailable."""

    return Rover(pins=pins, max_speed=max_speed)
