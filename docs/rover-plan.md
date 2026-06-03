# Rover Plan

Diamond is being rebuilt from a quadruped walker into a wheeled rover.

## Why

The MG90 servos can't lift the robot once the Waveshare UPS HAT battery pack is
mounted — walking would need stronger motors and a heavier power system. Wheels
draw a fraction of the power, are far simpler to get running, and give a stable
base for vision/audio experiments.

## Approach

A wheeled rover running [DonkeyCar](https://www.donkeycar.com/) on the Raspberry
Pi 5, driven by the existing Xbox controller, built toward a behavioral-cloning
vision policy. Reused as-is: the Pi 5, PCA9685, Waveshare UPS HAT, Xbox controller,
and the existing PCA9685/I2C and Xbox teleop code.

## Stage 1 — 4WD differential (parts ordered)

| Part | Qty | Notes |
|------|-----|-------|
| JGA25-370 12V 280rpm geared motor w/ encoder | 4 | bundle includes a 65mm 12mm-hex wheel, hex coupling, motor bracket |
| L298 dual H-bridge motor driver | 2 | one per side |
| 3S 11.1V 2200mAh LiPo | 1 | reused from the original walker design — check voltage and inspect for puffing before use |
| 3D-printed deck + drive sub-frame | — | printed on the Bambu A1 |

Skid-steer: four fixed wheels, turning by driving the two sides at different
speeds. The motor encoders are available for odometry; the vision policy itself
won't need them.

## Power

Two separate domains, common ground:

- **Muscle** — 3S LiPo (~11.1V) -> L298 -> motors
- **Brain** — Waveshare UPS HAT -> 5V -> Pi 5 (and the PCA9685)

Keeping motor power off the Pi's rail avoids brownout/reboot from motor noise.

## Wiring

- Two L298 boards, one per side, each driving that side's two motors. Controlled
  as two channels (left / right) over Pi GPIO — DonkeyCar's `DC_TWO_WHEEL_L298N`
  drivetrain.
- First bench wiring and motor test procedure:
  [motor-bringup-wiring.md](motor-bringup-wiring.md).
- The existing PCA9685 can stay connected on I2C, but it is not needed for the
  first L298 motor test. It cannot drive DC motors directly; it is reserved for
  later PWM outputs such as steering or a camera gimbal.
- The Pi 5 changed its GPIO subsystem (RP1 chip); use a Pi-5-compatible GPIO
  backend (`lgpio`) for the H-bridge. The PCA9685 I2C path is unaffected.

## Roadmap

1. **4WD differential** — Stage 1, parts ordered.
2. **Ackermann steering** — reuse the motors + L298 (DonkeyCar
   `DC_STEERING_THROTTLE`) and add one steering servo on the PCA9685. Ackermann
   doesn't scrub, so the 280rpm motors suit it well.
3. **Suspension**, then **camera** (Pi Camera 3), **mic**, **IMU**.
4. **Vision policy** — record driving data, train a behavioral-cloning policy.

## Standards

Chosen to keep parts reusable across stages:

- **Wheels** — 12mm hex hub (hshop V2 65mm / V3 85mm / V4 130mm are interchangeable).
- **Power connector** — XT60.
- The 12V / 3S power domain also matches a LeRobot LeKiwi base, so the battery
  carries over to that side of the bench.
