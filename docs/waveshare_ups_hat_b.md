# Waveshare UPS HAT (B) - Technical Documentation

**Source**: https://www.waveshare.com/wiki/UPS_HAT_(B)

## Core Specifications

- **Power Output**: 5V at up to 5A continuous current (4A recommended max for sustained use)
- **Battery**: Two 18650 Li-ion cells (2600mAh, not included)
- **Charger**: 8.4V 2A input
- **Communication**: I2C bus protocol
- **Dimensions**: 56 × 85mm with 3.0mm mounting holes
- **Compatible with**: Raspberry Pi 3/3B+/4B/5 and similar models

## Key Features

- I2C bus communication for monitoring battery voltage, current, power, and remaining capacity in real-time
- Overcharge/discharge protection
- Over current protection
- Short circuit protection
- Reverse polarity protection
- Equalizing charge feature
- Onboard USB 5V output port for powering additional devices
- Visual indicators for charging status and battery connection warnings

## Setup Instructions

### Enable I2C

1. Open terminal and run: `sudo raspi-config`
2. Navigate to: Interfacing Options → I2C
3. Select: Yes
4. Reboot

### Installation & Testing

```bash
sudo apt-get install p7zip
wget https://files.waveshare.com/upload/4/4a/UPS_HAT_B.7z
7zr x UPS_HAT_B.7z -r -o./
cd UPS_HAT_B
python3 INA219.py
```

## Battery Monitoring (INA219.py)

The included `INA219.py` library provides real-time monitoring via I2C:

- **Voltage**: Battery voltage reading
- **Current**:
  - Negative values = discharging (powering the Pi)
  - Positive values = charging
- **Power**: Current power draw/charge rate
- **Capacity**: Remaining battery capacity (may fluctuate during charging)

## Critical Operational Notes

⚠️ **SAFETY WARNINGS**:
- Turn power switch to OFF before connecting batteries
- Press Boot button to activate circuit when mounting batteries initially
- Monitor WARNING LED - illumination indicates reversed battery polarity
- Only use the included 8.4V 2A power supply for charging
- Lithium batteries can cause fire or injury if misused
- Do not mix old/new batteries
- Replace batteries after maximum cycle life or two years (whichever comes first)

**Thermal Management**:
- Sustained 5A operation generates significant heat
- Recommended maximum continuous draw: 4A

## Pin Connections

- **Pin 2** (5V): Main power output to devices (connects to V+ on PCA9685 in our setup)
- **GPIO pins 1/3/5/9**: I2C communication with Raspberry Pi

## Data Interpretation Notes

- Battery capacity readings may fluctuate during charging
- Capacity may exceed actual battery capacity due to voltage-based measurement methods
- Current draw varies based on Pi model and connected peripherals
