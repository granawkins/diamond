import time
import board, busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

class Diamond:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50

        self.servo0 = servo.Servo(self.pca.channels[0], min_pulse=500, max_pulse=2500)
        self.servo1 = servo.Servo(self.pca.channels[1], min_pulse=500, max_pulse=2500)

        self.reset()

    def reset(self):
        self.servo0.angle = 52
        self.servo1.angle = 52

    def forward(self):
        self.servo0.angle = 30
        time.sleep(0.5)
        self.servo1.angle = 40
        time.sleep(0.5)
        self.servo0.angle = 60
        time.sleep(0.5)
        self.servo1.angle = 60
        time.sleep(0.5)