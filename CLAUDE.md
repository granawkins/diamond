# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Diamond is a quadruped robot running on Raspberry Pi 5 that controls MG90 servos through a PCA9685 PWM controller via I2C.

## Hardware Setup

- **Controller**: Raspberry Pi 5 with I2C on GPIO pins 1/3/5/9
- **Power**: Waveshare UPS HAT with two 18650 cells (8.4V charger). The HAT's 5V output (pin 2) connects directly to V+ on the PCA9685
- **PWM Driver**: PCA9685 board (16 channels at 50Hz)
- **Servos**: MG90 servos with min_pulse=500, max_pulse=2500
- **Channel mapping**: 0-3 front left, 4-7 front right, 8-11 back left, 12-15 back right

## Development

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Test single servo
python servo-test.py

# Run robot
python diamond.py
```

## Code Structure

**`diamond.py`**: Main `Diamond` class that initializes I2C/PCA9685 and controls servos. Currently implements 2 servos with `reset()` and `forward()` methods.

**`servo-test.py`**: Utility to test individual servo connections before integrating into main class.

**Note**: Code requires Raspberry Pi 5 hardware with connected I2C devices.
