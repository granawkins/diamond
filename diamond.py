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
    # body.update()
    time.sleep(1/hz)
