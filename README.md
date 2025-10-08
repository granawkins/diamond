# Diamond

Diamond is a quadruped robot, and these are all the files related to its design and software. 

## Electronics

### System Diagram
```
Wall Power (USB-C) ────────────────────────┐
                                           │
Battery: 3S Li-ion 2200mAh (11.1V)         │
        │                                  │
        ├─→ INA219 (I2C Battery Monitor)  │
        │          │                       │
        │          └─→ SCL ───────────┐    │
        │              SDA ───────┐   │    │
        │                         │   │    │
        └─→ UBEC 5V                │   │    │
                │                  │   │    │
                ├─→ Relay (GPIO17) │   │    │
                │       │           │   │    │
                │       └─→ PCA9685 │   │    │
                │              │    │   │    │
                │              ├─→ SCL 5────┤
                │              ├─→ SDA 3────┤
                │              └─→ VCC 1────┤
                │                           │
                └───────────────────────────┴─→ Raspberry Pi 5 8GB
                                                    │
                                    GPIO3 ←─ Shutdown Button (to GND)
                                    GPIO17 ─→ Servo Relay Control
                                    SD Card 16GB

PCA9685 Servo Channels:
  0-3:   Front Left  (lower hip, upper hip, shoulder, -)
  4-7:   Front Right (lower hip, upper hip, shoulder, -)
  8-11:  Back Left   (lower hip, upper hip, shoulder, -)
  12-15: Back Right  (lower hip, upper hip, shoulder, -)
```

### Power Management Features

**Dual Power Mode:**
- **Battery Mode**: 3S Li-ion → UBEC → Pi + Servos
- **Wall Mode**: USB-C → Pi only (servos disabled or separate power)

**Battery Monitoring (INA219):**
- Voltage, current, and power measurement via I2C
- Battery percentage estimation
- Future: LED indicator control

**Safe Shutdown:**
- Shutdown button on GPIO3 (hold 2 seconds)
- Automatically disables servo power before Pi shutdown
- GPIO3 can wake Pi from halt state

**Servo Power Control:**
- Relay on GPIO17 controls servo power
- Prevents servo jitter during shutdown
- Can disable servos when running on wall power only

## Roadmap
- Better leg design
- Power switch/button
- Full body design
- Control programming
- VLM integration
- VLA / RLing
