import time
import board, busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

class Diamond:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = 50

        servo0 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500)
        servo1 = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500)

        servo0.angle = 0  # horizontal, left
        servo1.angle = 0  # vertical, up

        servo0.angle = 52
        servo1.angle = 38  # legs perpendicular

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