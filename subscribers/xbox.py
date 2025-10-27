"""
Xbox Wireless Controller (MAC: 40:8E:2C:4A:25:C9)

Fix for connect/disconnect loop:
- Modified /etc/bluetooth/main.conf: ControllerMode=dual, FastConnectable=true, Privacy=device
- Controller is paired, bonded, and trusted - should auto-reconnect when powered on
- Creates /dev/input/event5 (main), event6 (consumer), event7 (keyboard), js0 (joystick)
"""

import time
from evdev import InputDevice, categorize, ecodes, list_devices

command_func = None

def connect():
    """Find and connect to Xbox Wireless Controller"""
    device = InputDevice('/dev/input/event5')
    # TODO: didn't work
    # for device_path in list_devices():
    #     if "Xbox Wireless Controller" in device.name:
    #         device = InputDevice(device_path)
    #         print(f"Found Xbox controller: {device.name} at {device.path}")
    #         return device
    return None

def init(command_fn):
    """Initialize with command callback"""
    global command_func
    command_func = command_fn

def run():
    """Main loop - connect to controller and listen for d-pad input"""
    controller = None

    while True:
        # Try to connect if not connected
        if controller is None:
            controller = connect()
            if controller is None:
                print("Xbox controller not found, retrying in 5s...")
                time.sleep(5)
                continue

        try:
            # Listen for events
            for event in controller.read_loop():
                """
                down: code 17 value 1
                up: code 17 value -1
                right: code 16 value 1
                left: code 16 value -1
                """
                if event.code == 17 and event.value == 1:
                    if command_func:
                        command_func("down")
                elif event.code == 17 and event.value == -1:
                    if command_func:
                        command_func("up")
        except (OSError, IOError) as e:
            print(f"Controller disconnected: {e}")
            controller = None
            time.sleep(2)
