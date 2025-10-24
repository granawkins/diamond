#!/usr/bin/env python3
"""
Shutdown button handler for Waveshare UPS HAT (B)
Monitors the BOOT button and triggers clean shutdown when pressed.
"""
import time
import subprocess
from gpiozero import Button
from signal import pause

# Common GPIO pins used by Waveshare UPS HATs
# Try GPIO4 first (common for boot/shutdown buttons)
# Adjust if your HAT uses a different pin (GPIO19, GPIO17, etc.)
BUTTON_PIN = 4

# Hold duration in seconds for shutdown
HOLD_TIME = 2.0

def cleanup_before_shutdown():
    """
    Perform cleanup operations before shutdown.
    Add your cleanup code here (e.g., reset servos, close connections, etc.)
    """
    print("Performing cleanup before shutdown...")

    # Example: Reset Diamond servos to safe position
    try:
        import diamond
        robot = diamond.Diamond()
        print("Resetting servos to safe position...")
        robot.reset()
        time.sleep(0.5)
        print("Servos reset complete.")
    except Exception as e:
        print(f"Error during servo cleanup: {e}")

    # Add any other cleanup here
    print("Cleanup complete.")

def shutdown_system():
    """Trigger system shutdown"""
    print("Initiating system shutdown...")
    cleanup_before_shutdown()
    subprocess.run(['sudo', 'shutdown', '-h', 'now'])

def on_button_press():
    """Called when button is first pressed"""
    print("Button pressed - checking hold duration...")

def on_button_hold():
    """Called when button is held for HOLD_TIME seconds"""
    print(f"Button held for {HOLD_TIME} seconds - shutting down!")
    shutdown_system()

def on_button_release():
    """Called when button is released"""
    print("Button released.")

def main():
    print(f"Shutdown button monitor started on GPIO{BUTTON_PIN}")
    print(f"Hold button for {HOLD_TIME} seconds to trigger shutdown.")

    # Create button with internal pull-up resistor
    # bounce_time prevents false triggers from electrical noise
    button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)

    # Set up event handlers
    button.when_pressed = on_button_press
    button.when_held = on_button_hold
    button.when_released = on_button_release
    button.hold_time = HOLD_TIME

    # Keep the script running
    print("Monitoring button presses... (Ctrl+C to exit)")
    try:
        pause()
    except KeyboardInterrupt:
        print("\nShutdown monitor stopped.")

if __name__ == "__main__":
    main()
