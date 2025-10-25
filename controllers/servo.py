from adafruit_motor import servo as adafruit_servo

# Servo configuration by channel
SERVO_CONFIG = {
    0: {"name": "front_left_lower_hip", "45_deg": 41, "135_deg": 161},
    1: {"name": "front_left_upper_hip", "45_deg": 36, "135_deg": 148},
    2: {"name": "front_left_shoulder", "45_deg": 31, "135_deg": 143},
    # 3: empty
    4: {"name": "back_left_lower_hip", "45_deg": 36, "135_deg": 148},
    5: {"name": "back_left_upper_hip", "45_deg": 30, "135_deg": 145},
    6: {"name": "back_left_shoulder", "45_deg": 41, "135_deg": 158},
    # 7: empty
    8: {"name": "back_right_lower_hip", "45_deg": 33, "135_deg": 143},
    9: {"name": "back_right_upper_hip", "45_deg": 30, "135_deg": 142},
    10: {"name": "back_right_shoulder", "45_deg": 38, "135_deg": 156},
    # 11: empty
    12: {"name": "front_right_lower_hip", "45_deg": 45, "135_deg": 152},
    13: {"name": "front_right_upper_hip", "45_deg": 41, "135_deg": 145},
    14: {"name": "front_right_shoulder", "45_deg": 31, "135_deg": 143},
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
        self._angle = 90
        self._45_deg = config["45_deg"]
        self._135_deg = config["135_deg"]

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value, calibrate=True):
        if calibrate:
            # interpolate between 45_deg and 135_deg
            angle = self._45_deg + (self._135_deg - self._45_deg) * (value - 45) / 90
        else:
            angle = value
        self.servo.angle = angle
        self._angle = angle
