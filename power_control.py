"""
Power control for safe shutdown and servo power management.
Handles shutdown button and relay control for servo power.
"""
import time
import RPi.GPIO as GPIO
import subprocess

# GPIO pin configuration
SHUTDOWN_BUTTON_PIN = 3  # GPIO3 can wake Pi from halt
SERVO_RELAY_PIN = 17     # Controls relay for servo power

class PowerControl:
    def __init__(self, shutdown_pin=SHUTDOWN_BUTTON_PIN, relay_pin=SERVO_RELAY_PIN):
        """
        Initialize power control.
        
        Args:
            shutdown_pin: GPIO pin for shutdown button (default: GPIO3)
            relay_pin: GPIO pin for servo power relay (default: GPIO17)
        """
        self.shutdown_pin = shutdown_pin
        self.relay_pin = relay_pin
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Shutdown button (pull-up, active low)
        GPIO.setup(self.shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Servo relay (active high - HIGH = servos powered)
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.HIGH)  # Start with servos powered
        
        # Button press tracking
        self.button_pressed_time = None
        self.shutdown_initiated = False
        
    def enable_servos(self):
        """Enable power to servos via relay."""
        GPIO.output(self.relay_pin, GPIO.HIGH)
        print("Servo power: ENABLED")
    
    def disable_servos(self):
        """Disable power to servos via relay."""
        GPIO.output(self.relay_pin, GPIO.LOW)
        print("Servo power: DISABLED")
    
    def check_shutdown_button(self):
        """
        Check if shutdown button is pressed.
        Requires 2-second hold to prevent accidental shutdown.
        
        Returns:
            bool: True if shutdown should be initiated
        """
        button_state = GPIO.input(self.shutdown_pin)
        
        # Button pressed (active low)
        if button_state == GPIO.LOW:
            if self.button_pressed_time is None:
                self.button_pressed_time = time.time()
                print("Shutdown button pressed...")
            else:
                # Check if held for 2 seconds
                hold_time = time.time() - self.button_pressed_time
                if hold_time >= 2.0 and not self.shutdown_initiated:
                    print("Shutdown button held for 2 seconds - initiating shutdown")
                    return True
        else:
            # Button released
            if self.button_pressed_time is not None:
                hold_time = time.time() - self.button_pressed_time
                if hold_time < 2.0:
                    print("Shutdown button released (held for {:.1f}s - need 2s)".format(hold_time))
                self.button_pressed_time = None
        
        return False
    
    def shutdown(self):
        """
        Perform safe shutdown sequence:
        1. Disable servo power
        2. Wait briefly
        3. Shutdown Pi
        """
        if self.shutdown_initiated:
            return
        
        self.shutdown_initiated = True
        
        print("\n=== INITIATING SHUTDOWN SEQUENCE ===")
        print("1. Disabling servo power...")
        self.disable_servos()
        
        print("2. Waiting 1 second...")
        time.sleep(1)
        
        print("3. Shutting down Raspberry Pi...")
        subprocess.run(["sudo", "shutdown", "-h", "now"])
    
    def cleanup(self):
        """Clean up GPIO resources."""
        GPIO.cleanup()
    
    def run(self):
        """
        Main loop - monitor shutdown button.
        Call this to start monitoring for shutdown.
        """
        print("Power Control Active")
        print("- Servos: ENABLED")
        print("- Shutdown: Hold button for 2 seconds")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                if self.check_shutdown_button():
                    self.shutdown()
                    break
                time.sleep(0.1)  # Check every 100ms
        except KeyboardInterrupt:
            print("\nExiting power control...")
        finally:
            self.cleanup()


if __name__ == "__main__":
    # Test power control
    power = PowerControl()
    power.run()
