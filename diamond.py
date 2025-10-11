import time
import board, busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

class Leg():
    def __init__(self, name, pca, lower_hip_channel, upper_hip_channel, shoulder_channel):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50

        self.lower_hip = servo.Servo(self.pca.channels[lower_hip_channel], min_pulse=500, max_pulse=2500)
        self.upper_hip = servo.Servo(self.pca.channels[upper_hip_channel], min_pulse=500, max_pulse=2500)
        self.shoulder = servo.Servo(self.pca.channels[shoulder_channel], min_pulse=500, max_pulse=2500)

        self.reset()

    def reset(self):
        self.lower_hip.angle = 52
        self.upper_hip.angle = 52
        self.shoulder.angle = 90

    def forward(self):
        self.lower_hip.angle = 30
        time.sleep(0.5)
        self.upper_hip.angle = 40
        time.sleep(0.5)
        self.lower_hip.angle = 60
        time.sleep(0.5)
        self.upper_hip.angle = 60
        time.sleep(0.5)


class Diamond():
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50

        self.legs = {
            "front_left": Leg("front_left", self.pca, 0, 1, 2),
            "front_right": Leg("front_right", self.pca, 4, 5, 6),
            "back_left": Leg("back_left", self.pca, 8, 9, 10),
            "back_right": Leg("back_right", self.pca, 12, 13, 14)
        }

    def reset(self):
        for leg in self.legs.values():
            leg.reset()

    def forward(self):
        for leg in self.legs.values():
            leg.forward()

    def bounce(self, n):
        for _ in range(n):
            for leg in self.legs.values():
                leg.lower_hip.angle = 30
                leg.upper_hip.angle = 30
            time.sleep(0.5)
            for leg in self.legs.values():
                leg.reset()