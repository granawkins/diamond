from adafruit_motor import servo as adafruit_servo

# Servo configuration by channel
SERVO_CONFIG = {
    0: {"name": "front_left_lower_hip"},
    1: {"name": "front_left_upper_hip"},
    2: {"name": "front_left_shoulder"},
    # 3: empty
    4: {"name": "back_left_lower_hip"},
    5: {"name": "back_left_upper_hip"},
    6: {"name": "back_left_shoulder"},
    # 7: empty
    8: {"name": "back_right_lower_hip"},
    9: {"name": "back_right_upper_hip"},
    10: {"name": "back_right_shoulder"},
    # 11: empty
    12: {"name": "front_right_lower_hip"},
    13: {"name": "front_right_upper_hip"},
    14: {"name": "front_right_shoulder"},
    # 15: empty
}

# Reverse lookup for API
CHANNEL_TO_NAME = {ch: cfg["name"] for ch, cfg in SERVO_CONFIG.items()}
NAME_TO_CHANNEL = {cfg["name"]: ch for ch, cfg in SERVO_CONFIG.items()}
MIN_PULSE = 500
MAX_PULSE = 2500

class Servo:
    def __init__(self, channel, pca):
        self.channel = channel
        config = SERVO_CONFIG[channel]
        self.name = config["name"]
        self.servo = adafruit_servo.Servo(
            pca.channels[channel],
            min_pulse=MIN_PULSE,
            max_pulse=MAX_PULSE
        )
        self.angle = 90

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self.servo.angle = value
        self._angle = value
