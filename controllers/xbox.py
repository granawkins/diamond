"""
Xbox Wireless Controller (MAC: 40:8E:2C:4A:25:C9)

Fix for connect/disconnect loop:
- Modified /etc/bluetooth/main.conf: ControllerMode=dual, FastConnectable=true, Privacy=device
- Controller is paired, bonded, and trusted - should auto-reconnect when powered on
- Creates /dev/input/event5 (main), event6 (consumer), event7 (keyboard), js0 (joystick)
"""

import asyncio
from enum import Enum
from evdev import InputDevice, ecodes


class Button(Enum):
    """Button events emitted by the controller"""
    # Face buttons
    A = "a"
    B = "b"
    X = "x"
    Y = "y"

    # D-pad
    DPAD_UP = "dpad_up"
    DPAD_DOWN = "dpad_down"
    DPAD_LEFT = "dpad_left"
    DPAD_RIGHT = "dpad_right"

    # Left joystick
    LEFT_STICK_UP = "left_stick_up"
    LEFT_STICK_DOWN = "left_stick_down"
    LEFT_STICK_LEFT = "left_stick_left"
    LEFT_STICK_RIGHT = "left_stick_right"

    # Right joystick
    RIGHT_STICK_UP = "right_stick_up"
    RIGHT_STICK_DOWN = "right_stick_down"
    RIGHT_STICK_LEFT = "right_stick_left"
    RIGHT_STICK_RIGHT = "right_stick_right"

    # Triggers
    LEFT_TRIGGER = "left_trigger"
    RIGHT_TRIGGER = "right_trigger"


class Controller:
    """Xbox Wireless Controller interface"""

    # Map raw event codes to Button enum
    _BUTTON_MAP = {
        304: Button.A,
        305: Button.B,
        307: Button.X,
        308: Button.Y,
    }

    # Joystick axes and trigger codes
    _LEFT_STICK_Y = 1   # ABS_Y
    _LEFT_STICK_X = 0   # ABS_X
    _RIGHT_STICK_Y = 4  # ABS_RY
    _RIGHT_STICK_X = 3  # ABS_RX
    _LEFT_TRIGGER = 2   # ABS_Z
    _RIGHT_TRIGGER = 5  # ABS_RZ
    _DPAD_X = 16        # ABS_HAT0X
    _DPAD_Y = 17        # ABS_HAT0Y

    # Thresholds for analog inputs
    _STICK_THRESHOLD = 20000  # Joystick deadzone
    _TRIGGER_THRESHOLD = 10   # Trigger activation threshold

    def __init__(self, device_path='/dev/input/event5'):
        self.device_path = device_path
        self.device = None
        self._stick_states = {}  # Track joystick state to detect changes
        self._trigger_states = {Button.LEFT_TRIGGER: False, Button.RIGHT_TRIGGER: False}

    def connect(self):
        """Connect to the controller device"""
        try:
            self.device = InputDevice(self.device_path)
            print(f"Connected to {self.device.name}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    async def events(self):
        """Async generator that yields button press events"""
        while True:
            # Try to connect if not connected
            if self.device is None:
                if not self.connect():
                    print("Controller not found, retrying in 5s...")
                    await asyncio.sleep(5)
                    continue

            try:
                # Read events from controller
                async for event in self.device.async_read_loop():
                    button_event = self._process_event(event)
                    if button_event:
                        yield button_event

            except (OSError, IOError) as e:
                print(f"Controller disconnected: {e}")
                self.device = None
                await asyncio.sleep(2)

    def _process_event(self, event):
        """Process raw event and return Button or None"""

        # Button presses (EV_KEY)
        if event.type == ecodes.EV_KEY and event.value == 1:  # Press only
            return self._BUTTON_MAP.get(event.code)

        # Analog inputs (EV_ABS)
        if event.type == ecodes.EV_ABS:
            # D-pad (digital -1/0/1 values)
            if event.code == self._DPAD_X:
                return self._handle_dpad(event.value, Button.DPAD_LEFT, Button.DPAD_RIGHT, 'dpad_x')
            if event.code == self._DPAD_Y:
                return self._handle_dpad(event.value, Button.DPAD_UP, Button.DPAD_DOWN, 'dpad_y')

            # Left stick
            elif event.code == self._LEFT_STICK_Y:
                return self._handle_stick_axis(event.value, Button.LEFT_STICK_UP, Button.LEFT_STICK_DOWN, 'left_y')
            elif event.code == self._LEFT_STICK_X:
                return self._handle_stick_axis(event.value, Button.LEFT_STICK_LEFT, Button.LEFT_STICK_RIGHT, 'left_x')

            # Right stick
            elif event.code == self._RIGHT_STICK_Y:
                return self._handle_stick_axis(event.value, Button.RIGHT_STICK_UP, Button.RIGHT_STICK_DOWN, 'right_y')
            elif event.code == self._RIGHT_STICK_X:
                return self._handle_stick_axis(event.value, Button.RIGHT_STICK_LEFT, Button.RIGHT_STICK_RIGHT, 'right_x')

            # Triggers
            elif event.code == self._LEFT_TRIGGER:
                return self._handle_trigger(event.value, Button.LEFT_TRIGGER)
            elif event.code == self._RIGHT_TRIGGER:
                return self._handle_trigger(event.value, Button.RIGHT_TRIGGER)

        return None

    def _handle_dpad(self, value, negative_button, positive_button, axis_key):
        """Handle D-pad - fires on press (value -1 or 1), not release (0)"""
        if value == -1:
            if self._stick_states.get(axis_key) != 'negative':
                self._stick_states[axis_key] = 'negative'
                return negative_button
        elif value == 1:
            if self._stick_states.get(axis_key) != 'positive':
                self._stick_states[axis_key] = 'positive'
                return positive_button
        else:
            # Reset state on release
            self._stick_states[axis_key] = None
        return None

    def _handle_stick_axis(self, value, negative_button, positive_button, axis_key):
        """Handle joystick axis movement - only trigger on first press"""
        if value < -self._STICK_THRESHOLD:
            if self._stick_states.get(axis_key) != 'negative':
                self._stick_states[axis_key] = 'negative'
                return negative_button
        elif value > self._STICK_THRESHOLD:
            if self._stick_states.get(axis_key) != 'positive':
                self._stick_states[axis_key] = 'positive'
                return positive_button
        else:
            # Reset state when returning to center
            self._stick_states[axis_key] = None
        return None

    def _handle_trigger(self, value, button):
        """Handle trigger press - only trigger on first press"""
        pressed = value > self._TRIGGER_THRESHOLD
        was_pressed = self._trigger_states[button]

        if pressed and not was_pressed:
            self._trigger_states[button] = True
            return button
        elif not pressed:
            self._trigger_states[button] = False

        return None


if __name__ == "__main__":
    async def test_controller():
        """Test the controller by printing all button events"""
        controller = Controller()
        print("Listening for controller events... (press Ctrl+C to exit)")

        async for button in controller.events():
            print(f"Button pressed: {button.value}")

    asyncio.run(test_controller())
