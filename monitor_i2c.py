#!/usr/bin/env python3
"""
Monitor I2C device 0x42 for changes when button is pressed.
Some UPS HATs use an onboard microcontroller to handle button input.
"""
import smbus2 as smbus
import time

I2C_BUS = 1
DEVICE_ADDR = 0x42

bus = smbus.SMBus(I2C_BUS)

print(f"Monitoring I2C device 0x{DEVICE_ADDR:02x} for button activity...")
print("Press the BOOT button and watch for changes.\n")
print("Scanning registers 0x00 to 0x20...\n")

# Store initial values
initial_values = {}
for reg in range(0x21):
    try:
        val = bus.read_byte_data(DEVICE_ADDR, reg)
        initial_values[reg] = val
    except:
        initial_values[reg] = None

print("Initial values captured. Press button now...\n")

try:
    while True:
        for reg in range(0x21):
            if initial_values[reg] is None:
                continue
            try:
                current_val = bus.read_byte_data(DEVICE_ADDR, reg)
                if current_val != initial_values[reg]:
                    print(f"*** CHANGE DETECTED! Register 0x{reg:02x}: 0x{initial_values[reg]:02x} -> 0x{current_val:02x} ***")
                    initial_values[reg] = current_val
            except:
                pass
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nMonitoring stopped.")
