import time
import board, busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

class Leg():
    def __init__(self, name, pca, lower_hip_channel, upper_hip_channel, shoulder_channel):
        self.name = name
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
        # Collect all servo positions first
        servo_commands = []
        for leg in self.legs.values():
            servo_commands.extend([
                (leg.lower_hip, 52),
                (leg.upper_hip, 52),
                (leg.shoulder, 90)
            ])
        
        # Execute all commands as quickly as possible
        for servo_obj, angle in servo_commands:
            servo_obj.angle = angle

    def up(self):
        # Collect all servo positions first
        servo_commands = []
        for leg in self.legs.values():
            if "right" in leg.name:
                servo_commands.extend([
                    (leg.upper_hip, 75),
                    (leg.lower_hip, 30),
                    # (leg.shoulder, 120)
                ])
            else:
                servo_commands.extend([
                    (leg.upper_hip, 30),
                    (leg.lower_hip, 75),
                    # (leg.shoulder, 60)
                ])
        
        # Execute all commands as quickly as possible
        for servo_obj, angle in servo_commands:
            servo_obj.angle = angle

    
    def dance(self, times):
        for _ in range(times):
            self.up()
            time.sleep(2)
            self.reset()
            time.sleep(2)

if __name__ == "__main__":
    diamond = Diamond()
    diamond.dance(10)