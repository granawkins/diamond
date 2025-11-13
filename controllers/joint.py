from adafruit_motor import servo as adafruit_servo

MIN_ANGLE = 0
MAX_ANGLE = 180

# Servo configuration by channel
SERVO_CONFIG = {
    "front_left_lower_hip": {"channel": 0, "m": 2.73, "b": 398},
    "front_left_upper_hip": {"channel": 1, "m": 1.5, "b": 270},
    "front_left_shoulder": {"channel": 2, "m": 1, "b": -12},
    # 3: empty
    "back_left_lower_hip": {"channel": 4, "m": 2.6, "b": 377},
    "back_left_upper_hip": {"channel": 5, "m": 1.46, "b": 256},
    "back_left_shoulder": {"channel": 6, "m": 1, "b": 4},
    # 7: empty
    "back_right_lower_hip": {"channel": 8, "m": -2.67, "b": -205},
    "back_right_upper_hip": {"channel": 9, "m": -1.22, "b": -73},
    "back_right_shoulder": {"channel": 10, "m": 1, "b": 7},
    # 11: empty
    "front_right_lower_hip": {"channel": 12, "m": -2.5, "b": -195},
    "front_right_upper_hip": {"channel": 13, "m": -1.16, "b": -55},
    "front_right_shoulder": {"channel": 14, "m": 1, "b": -13},
    # 15: empty
}

class Joint:
    _angle: float
    _actual: float

    def __init__(self, name, default, mode="SIM"):
        self.default = default
        self.servo = None

        config = SERVO_CONFIG[name]
        self.m = config["m"]
        self.b = config["b"]

        if mode == "LIVE":
            from controllers.pca import pca
            
            self.servo = adafruit_servo.Servo(
                pca.channels[config["channel"]],
                min_pulse=500,
                max_pulse=2500,
            )

        self.angle = default

    def reset(self):
        self.angle = self.default

    def state(self):
        return {
            "angle": self._angle,
            "actual": self._actual,
            "m": self.m,
            "b": self.b,
        }

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self._actual = min(MAX_ANGLE, max(MIN_ANGLE, self.m * value + self.b))
        if self.servo is not None:
            self.servo.angle = self._actual