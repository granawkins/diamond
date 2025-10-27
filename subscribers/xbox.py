"""
Control scheme:
    - lower/upper thigh and shoulder are controlled by lower joystick, upper joystick and l/r triggers.
    - a, b, x, y correspond to the four legs. y front-left, x back-left, b front-right, a back-right.
    - multiple limbs can be selected/moved at once
    - for now, increment one when knob or trigger is first pressed, ignore holding.
"""
import asyncio

from controllers.xbox import Controller

controller = Controller()
command_func = None

def init(command):
    controller.connect()
    global command_func
    command_func = command

async def _run():
    async for event in controller.events():
        print(event)

def run():
    asyncio.run(_run())