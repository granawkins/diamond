import time
import board, busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

servo0 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500)

for angle in range(0, 181, 30):
    servo0.angle = angle
    print("Angle:", angle)
    time.sleep(0.5)
