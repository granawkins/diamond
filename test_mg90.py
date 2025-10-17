import argparse
import time
import board, busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

def main(last_angle: int):

    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50

    s = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500)

    s.angle = 1
    time.sleep(2)
    s.angle = 180
    time.sleep(2)
    s.angle = last_angle


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("last_angle", type=int, nargs="?", default=90)
    args = parser.parse_args()
    main(args.last_angle)