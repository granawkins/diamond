"""
Control scheme:
    - lower/upper thigh and shoulder are controlled by lower joystick, upper joystick and l/r triggers.
    - a, b, x, y correspond to the four legs. y front-left, x back-left, b front-right, a back-right.
    - multiple limbs can be selected/moved at once
    - for now, increment one when knob or trigger is first pressed, ignore holding.
"""
import asyncio

from controllers.xbox import Controller, Button

controller = Controller()
command_func = None

# Track which legs are currently selected
selected_legs = set()

# Map buttons to leg names
BUTTON_TO_LEG = {
    Button.Y: "front_left",
    Button.X: "back_left",
    Button.B: "front_right",
    Button.A: "back_right",
}

# Map button to servo and delta
BUTTON_TO_SERVO = {
    Button.LEFT_STICK_UP: ("lower_hip", 5),
    Button.LEFT_STICK_DOWN: ("lower_hip", -5),
    Button.RIGHT_STICK_UP: ("upper_hip", 5),
    Button.RIGHT_STICK_DOWN: ("upper_hip", -5),
    Button.LEFT_TRIGGER: ("shoulder", -5),
    Button.RIGHT_TRIGGER: ("shoulder", 5),
}

def init(command):
    controller.connect()
    global command_func
    command_func = command

async def _run():
    async for event in controller.events():
        print(f"Event: {event}")

        # Handle up/down commands (D-pad)
        if event == Button.DPAD_UP:
            print("Sending command: up")
            command_func("up")
        elif event == Button.DPAD_DOWN:
            print("Sending command: down")
            command_func("down")

        elif event in (Button.LEFT_BUMPER, Button.RIGHT_BUMPER):
            print("Sending command: reset")
            command_func("reset")

        # Handle leg selection (face buttons)
        elif event in BUTTON_TO_LEG:
            leg = BUTTON_TO_LEG[event]
            if leg in selected_legs:
                selected_legs.remove(leg)
                print(f"Deselected: {leg}")
            else:
                selected_legs.add(leg)
                print(f"Selected: {leg}")
            print(f"Currently selected: {selected_legs}")

        # Handle servo control (joysticks and triggers)
        elif event in BUTTON_TO_SERVO:
            servo_name, delta = BUTTON_TO_SERVO[event]

            # Send command for each selected leg
            if selected_legs:
                for leg in selected_legs:
                    # Build command: set_<leg_name>_<servo_name>_<delta>
                    cmd = f"set_{leg}_{servo_name}_{delta}"
                    print(f"Sending command: {cmd}")
                    command_func(cmd)
            else:
                print(f"No legs selected - press A/B/X/Y to select legs")

def run():
    asyncio.run(_run())