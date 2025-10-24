import time
import queue
import threading
from controllers import pca, battery
from controllers.servo import Servo, SERVO_CONFIG
from subscribers import server, xbox

# Initialize 12 servos (skip channels 3, 7, 11, 15)
servos = {}
for channel in SERVO_CONFIG.keys():
    servo = Servo(channel, pca.pca)
    servos[servo.name] = servo

command_queue = queue.Queue()

def status():
    """Return current angles and battery stats"""
    servo_angles = {name: s.angle for name, s in servos.items()}
    battery_status = battery.status()
    return {
        "servos": servo_angles,
        "battery": battery_status
    }

def command(cmd):
    """Add command to queue"""
    command_queue.put(cmd)

def process_queue():
    """Process all commands in queue"""
    while not command_queue.empty():
        cmd = command_queue.get()
        servo_name = cmd.get("servo_name")
        angle = cmd.get("angle")
        if servo_name in servos:
            servos[servo_name].angle = angle

# Initialize and start server
server.init(status, command)
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()

# Start xbox controller (dummy for now)
xbox_thread = threading.Thread(target=xbox.run, daemon=True)
xbox_thread.start()

# Main loop at 1Hz
while True:
    process_queue()
    time.sleep(1)
