from adafruit_motor import servo as adafruit_servo

# Servo configuration by channel
SERVO_CONFIG = {
    "front_left_lower_hip": {"channel": 0, "default": 81},
    "front_left_upper_hip": {"channel": 1, "default": 83},
    "front_left_shoulder": {"channel": 2, "default": 78},
    # 3: empty
    "back_left_lower_hip": {"channel": 4, "default": 97},
    "back_left_upper_hip": {"channel": 5, "default": 64},
    "back_left_shoulder": {"channel": 6, "default": 94},
    # 7: empty
    "back_right_lower_hip": {"channel": 8, "default": 92},
    "back_right_upper_hip": {"channel": 9, "default": 101},
    "back_right_shoulder": {"channel": 10, "default": 97},
    # 11: empty
    "front_right_lower_hip": {"channel": 12, "default": 89},
    "front_right_upper_hip": {"channel": 13, "default": 101},
    "front_right_shoulder": {"channel": 14, "default": 77},
    # 15: empty
}

class Joint:
    def __init__(self, name, mode="SIM"):
        if mode == "LIVE":
            from controllers.pca import pca
            
            config = SERVO_CONFIG[name]
            self.servo = adafruit_servo.Servo(
                pca.channels[config["channel"]],
                min_pulse=500,
                max_pulse=2500,
            )
            self.default = config["default"]
            return
        else:
            self.servo = None
            self.default = 90

    def reset(self):
        self.angle = self.default

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if self.servo is not None:
            self.servo.angle = value
        self._angle = value