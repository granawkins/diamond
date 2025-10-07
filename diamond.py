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

        # Set initial angles: servo horns perpendicular, leg neutral
        self.servo0.angle = 52
        self.servo1.angle = 38

    def demo(self):
        # Cycle continuously through all angles 45 to 135 in steps of 15
        while True:
            for angle in range(45, 135, 15):
                self.servo0.angle = angle
                self.servo1.angle = angle
                time.sleep(0.1)
            for angle in range(135, 45, -15):
                self.servo0.angle = angle
                self.servo1.angle = angle
                time.sleep(0.1)