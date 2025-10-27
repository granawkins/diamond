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
        elif cmd.startswith("set_"):
            parts = cmd.split("_")
            delta = int(parts[-1])
            leg_name = f"{parts[1]}_{parts[2]}"
            servo_name = "_".join(parts[3:-1])

            # Map servo name to index in target_angles tuple
            servo_index = {"lower_hip": 0, "upper_hip": 1, "shoulder": 2}[servo_name]

            # Apply delta to target with 45-135 limits
            current_target = list(body.target_angles[leg_name])
            current_target[servo_index] += delta
            current_target[servo_index] = max(45, min(135, current_target[servo_index]))
            body.target_angles[leg_name] = tuple(current_target)
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
    body.step()
    time.sleep(1/hz)
