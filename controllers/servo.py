from adafruit_motor import servo as adafruit_servo

# Servo configuration by channel
SERVO_CONFIG = {
    0: {"name": "front_left_lower_hip", "min_pulse": 500, "max_pulse": 2500},
    1: {"name": "front_left_upper_hip", "min_pulse": 500, "max_pulse": 2500},
    2: {"name": "front_left_shoulder", "min_pulse": 500, "max_pulse": 2500},
    # 3: empty
    4: {"name": "back_left_lower_hip", "min_pulse": 500, "max_pulse": 2500},
    5: {"name": "back_left_upper_hip", "min_pulse": 500, "max_pulse": 2500},
    6: {"name": "back_left_shoulder", "min_pulse": 500, "max_pulse": 2500},
    # 7: empty
    8: {"name": "back_right_lower_hip", "min_pulse": 500, "max_pulse": 2500},
    9: {"name": "back_right_upper_hip", "min_pulse": 500, "max_pulse": 2500},
    10: {"name": "back_right_shoulder", "min_pulse": 500, "max_pulse": 2500},
    # 11: empty
    12: {"name": "front_right_lower_hip", "min_pulse": 500, "max_pulse": 2500},
    13: {"name": "front_right_upper_hip", "min_pulse": 500, "max_pulse": 2500},
    14: {"name": "front_right_shoulder", "min_pulse": 500, "max_pulse": 2500},
    # 15: empty
}

# Reverse lookup for API
CHANNEL_TO_NAME = {ch: cfg["name"] for ch, cfg in SERVO_CONFIG.items()}
NAME_TO_CHANNEL = {cfg["name"]: ch for ch, cfg in SERVO_CONFIG.items()}

class Servo:
    def __init__(self, channel, pca):
        self.channel = channel
        config = SERVO_CONFIG[channel]
        self.name = config["name"]
        self.servo = adafruit_servo.Servo(
            pca.channels[channel],
            min_pulse=config["min_pulse"],
            max_pulse=config["max_pulse"]
        )
        self._angle = 90

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self.servo.angle = value
        self._angle = value
