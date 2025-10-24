#!/usr/bin/env python3
"""
Comprehensive GPIO scanner - monitors ALL GPIO pins for button presses.
This will help identify which pin the BOOT button is connected to.
"""
import time
import sys

try:
    from gpiozero import Button
    from gpiozero.pins.lgpio import LGPIOFactory
except ImportError:
    print("Installing required library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lgpio"])
    from gpiozero import Button
    from gpiozero.pins.lgpio import LGPIOFactory

from signal import pause

# All available GPIO pins on Raspberry Pi 5
# BCM numbering
ALL_GPIOS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

buttons = []
detected_pins = []

def make_handler(pin):
    """Create a handler function for a specific pin"""
    def handler():
        timestamp = time.strftime("%H:%M:%S")
        print(f"\n{'='*50}")
        print(f"[{timestamp}] *** BUTTON PRESS DETECTED on GPIO{pin} ***")
        print(f"{'='*50}\n")
        if pin not in detected_pins:
            detected_pins.append(pin)
    return handler

print("="*60)
print("COMPREHENSIVE GPIO BUTTON SCANNER")
print("="*60)
print(f"\nScanning {len(ALL_GPIOS)} GPIO pins...")
print("This will monitor all available GPIO pins for button activity.\n")

# Set up listeners on all GPIO pins
factory = LGPIOFactory()
successful = []
failed = []

for pin in ALL_GPIOS:
    try:
        # Try with pull_up=True (button connects to GND when pressed)
        btn = Button(pin, pull_up=True, bounce_time=0.05, pin_factory=factory)
        btn.when_pressed = make_handler(pin)
        buttons.append(btn)
        successful.append(pin)
    except Exception as e:
        failed.append((pin, str(e)))

print(f"✓ Successfully monitoring {len(successful)} pins:")
for i in range(0, len(successful), 8):
    print(f"  {', '.join([f'GPIO{p}' for p in successful[i:i+8]])}")

if failed:
    print(f"\n✗ Could not monitor {len(failed)} pins (likely in use by I2C/SPI/etc):")
    for pin, err in failed[:3]:  # Show first 3 failures
        print(f"  GPIO{pin}: {err[:50]}")

print("\n" + "="*60)
print("PRESS THE BOOT BUTTON NOW")
print("="*60)
print("\nWatching for button presses... (Press Ctrl+C to exit)\n")

try:
    pause()
except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print("SCAN COMPLETE")
    print("="*60)
    if detected_pins:
        print(f"\n✓ Button detected on: {', '.join([f'GPIO{p}' for p in detected_pins])}")
        print(f"\nUpdate BUTTON_PIN = {detected_pins[0]} in shutdown_button.py")
    else:
        print("\n✗ No button presses detected.")
        print("\nPossible reasons:")
        print("  1. Button is on a pin that's already in use (I2C, etc)")
        print("  2. Button requires pull_down instead of pull_up")
        print("  3. Button is not a simple GPIO connection")
        print("\nTry running with sudo: sudo python scan_all_gpios.py")
    print("="*60)
