import time
import queue
import threading
from controllers.body import Body
import subscribers.server as server

command_queue = queue.Queue()

mode = "SIM"

body = Body()

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
        elif cmd == "front_up":
            body.front_up()
        elif cmd == "back_up":
            body.back_up()
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
server.init(body.state, command)
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()

# Initialize and start xbox controller
if mode == "LIVE":
    from subscribers.game_controller import game_controller
    
    game_controller.init(command)
    game_controller_thread = threading.Thread(target=game_controller.run, daemon=True)
    game_controller_thread.start()

hz = 20
while True:
    process_queue()
    body.step()
    time.sleep(1/hz)
