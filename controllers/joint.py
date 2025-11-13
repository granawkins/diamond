from adafruit_motor import servo as adafruit_servo

# Servo configuration by channel
SERVO_CONFIG = {
    "front_left_lower_hip": {"channel": 0, "m": -1, "b": 0},
    "front_left_upper_hip": {"channel": 1, "m": -1, "b": 0},
    "front_left_shoulder": {"channel": 2, "m": 1, "b": -12},
    # 3: empty
    "back_left_lower_hip": {"channel": 4, "m": -1, "b": 0},
    "back_left_upper_hip": {"channel": 5, "m": -1, "b": 0},
    "back_left_shoulder": {"channel": 6, "m": 1, "b": 4},
    # 7: empty
    "back_right_lower_hip": {"channel": 8, "m": -1, "b": 0},
    "back_right_upper_hip": {"channel": 9, "m": -1, "b": 0},
    "back_right_shoulder": {"channel": 10, "m": 1, "b": 7},
    # 11: empty
    "front_right_lower_hip": {"channel": 12, "m": -1, "b": 0},
    "front_right_upper_hip": {"channel": 13, "m": -1, "b": 0},
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
        self._actual = self.m * value + self.b
        if self.servo is not None:
            self.servo.angle = self._actual