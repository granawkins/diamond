import time
import queue
import threading
from controllers import battery
from controllers.body import Body
from subscribers import server, xbox

command_queue = queue.Queue()

body = Body()

def status():
    """Return current angles and battery stats"""
    legs_status = {name: l.angles for name, l in body.legs.items()}
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
        if cmd == "reset":
            body.reset()
        elif cmd == "up":
            body.up()
        elif cmd == "down":
            body.down()
        else:
            print(f"Invalid command: {cmd}")

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
