import os
import time
import queue
import threading
from controllers.body import Body
import subscribers.server as server

command_queue = queue.Queue()

# Check if it's a Raspberry PI
if os.path.exists("/proc/cpuinfo"):
    with open("/proc/cpuinfo", "r") as f:
        if "Raspberry Pi" in f.read():
            mode = "LIVE"
        else:
            mode = "SIM"
else:
    mode = "SIM"

body = Body(mode)
update_enabled = True

def command(cmd):
    """Add command to queue"""
    if cmd == "toggle_update":
        global update_enabled
        update_enabled = not update_enabled
        print(f"Update enabled: {update_enabled}")
    command_queue.put(cmd)

def get_state():
    return {
        **body.state(),
        "update_enabled": update_enabled,
    }

def process_queue():
    """Process all commands in queue"""
    while not command_queue.empty():
        cmd = command_queue.get()
        body.command(cmd)

# Initialize and start server
server.init(get_state, command)
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()

# Initialize and start xbox controller
if mode == "LIVE":
    import subscribers.game_controller as game_controller
    
    game_controller.init(command)
    game_controller_thread = threading.Thread(target=game_controller.run, daemon=True)
    game_controller_thread.start()

hz = 12
while True:
    process_queue()
    if update_enabled:
        body.update()
    time.sleep(1/hz)
