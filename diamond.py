import time
import queue
import threading
from controllers import pca, battery
from controllers.leg import Leg
from subscribers import server, xbox

# Initialize 12 servos (skip channels 3, 7, 11, 15)
legs = {
    "front_left": Leg("front_left", pca.pca),
    "back_left": Leg("back_left", pca.pca),
    "back_right": Leg("back_right", pca.pca),
    "front_right": Leg("front_right", pca.pca),
}

command_queue = queue.Queue()

def status():
    """Return current angles and battery stats"""
    legs_status = {name: l.angles for name, l in legs.items()}
    battery_status = battery.status()
    return {
        "legs": legs_status,
        "battery": battery_status
    }

def command(cmd):
    """Add command to queue"""
    command_queue.put(cmd)

def process_queue():
    """Process all commands in queue"""
    while not command_queue.empty():
        cmd = command_queue.get()
        leg_name = cmd.get("leg_name")
        if leg_name not in legs:
            print(f"Invalid leg name: {leg_name}")
        elif "angles" in cmd:
            legs[leg_name].angles = cmd.get("angles")
        elif "reset" in cmd:
            legs[leg_name].reset()

# Initialize and start server
server.init(status, command)
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()

# Start xbox controller (dummy for now)
xbox_thread = threading.Thread(target=xbox.run, daemon=True)
xbox_thread.start()

hz = 20
while True:
    process_queue()
    time.sleep(1/hz)
