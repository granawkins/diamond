#!/usr/bin/env python3
import sys
import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

def reset_servo(servo_number):
    """Reset a specific servo by moving it to 180 degrees, then to 1 degree."""
    try:
        # Initialize I2C and PCA9685
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = 50
        
        # Create servo object for the specified channel
        servo_obj = servo.Servo(pca.channels[servo_number], min_pulse=500, max_pulse=2500)
        
        print(f"Resetting servo {servo_number}...")
        
        # Move to 180 degrees
        print("Moving to 180 degrees...")
        servo_obj.angle = 180
        time.sleep(1)
        
        # Move to 1 degree
        print("Moving to 1 degree...")
        servo_obj.angle = 1
        time.sleep(1)
        
        print(f"Servo {servo_number} reset complete!")
        
    except Exception as e:
        print(f"Error resetting servo {servo_number}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reset_servo.py <servo_number>")
        print("Example: python reset_servo.py 0")
        sys.exit(1)
    
    try:
        servo_num = int(sys.argv[1])
        if servo_num < 0 or servo_num > 15:  # PCA9685 has 16 channels (0-15)
            print("Error: Servo number must be between 0 and 15")
            sys.exit(1)
        
        reset_servo(servo_num)
        
    except ValueError:
        print("Error: Servo number must be a valid integer")
        sys.exit(1)

