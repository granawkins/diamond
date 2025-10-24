#!/usr/bin/env python3
"""
Test script to detect which GPIO pin the BOOT button is connected to.
This will monitor multiple common GPIO pins used by Waveshare UPS HATs.
"""
from gpiozero import Button
from signal import pause
import time

# Common GPIO pins used by Waveshare UPS HATs for buttons
# GPIO4, GPIO17, GPIO19, GPIO27 are most common
TEST_PINS = [4, 17, 19, 27]

buttons = []

def make_handler(pin):
    """Create a handler function for a specific pin"""
    def handler():
        print(f"*** BUTTON DETECTED on GPIO{pin} ***")
    return handler

print("Button detection test starting...")
print(f"Testing GPIO pins: {TEST_PINS}")
print("Press the BOOT button to see which pin detects it.\n")

# Set up listeners on all test pins
for pin in TEST_PINS:
    try:
        btn = Button(pin, pull_up=True, bounce_time=0.1)
        btn.when_pressed = make_handler(pin)
        buttons.append(btn)
        print(f"✓ Monitoring GPIO{pin}")
    except Exception as e:
        print(f"✗ Could not monitor GPIO{pin}: {e}")

print("\nPress the BOOT button now... (Ctrl+C to exit)\n")

try:
    pause()
except KeyboardInterrupt:
    print("\n\nTest stopped.")
    print("If you saw '*** BUTTON DETECTED ***', use that GPIO pin number")
    print("in shutdown_button.py (update the BUTTON_PIN variable).")
