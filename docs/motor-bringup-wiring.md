# Motor Bring-up Wiring

This is the first wiring pass for proving the Raspberry Pi can command the four
DC drive motors through the two L298 H-bridge boards.

The current repo plan says Raspberry Pi 5, while the bench inventory says
Raspberry Pi 4. The GPIO pinout used below works on both Pi 4 and Pi 5.

## Parts

| Part | Qty | Purpose |
|------|-----|---------|
| Raspberry Pi 4 or 5 | 1 | Motor controller host |
| Waveshare UPS HAT with 2x 18650 cells | 1 | Pi power only |
| PCA9685 PWM servo driver | 1 | Existing board; optional for this first motor test |
| JGA25-370 12V 280rpm DC gearmotor | 4 | Drive motors |
| L298N dual H-bridge driver board | 2 | One board per side |
| 3S LiPo battery, nominal 11.1V | 1 | Motor power only |
| XT60 splitter or power distribution | 1 | Feeds both L298 motor inputs |
| Female-female jumper wires | several | Pi GPIO to L298 inputs |

Do not power the motors from the Pi, UPS HAT, or GPIO header. The Pi and motors
use separate power domains with a shared ground.

## PCA9685 Role

The PCA9685 is not needed for the first "can the Pi command the motors" test.
The L298 boards need two direction signals plus one PWM speed signal per side,
and the Pi can provide those directly from GPIO.

Keep the PCA9685 installed only if it is already part of the Pi/HAT stack and its
power wiring is known-good. Do not connect the motors to the PCA9685. It is a PWM
signal board for servos and control inputs, not a motor power driver.

For this stage, the PCA9685 is reserved for later accessories:

- steering servo if the rover moves to Ackermann steering
- camera gimbal servo
- other small PWM-controlled devices

There is an alternate wiring option where the PCA9685 provides the L298 `ENA` and
`ENB` PWM signals while Pi GPIO provides direction. That is useful if we want to
save Pi PWM pins later, but it adds another moving part during bring-up. The first
test should keep the PCA9685 out of the motor loop.

## Power Layout

```text
                 Brain power domain

  2x 18650 cells
       |
       v
  Waveshare UPS HAT
       |
       | 5V through HAT/header
       v
  Raspberry Pi 4/5
       |
       | optional I2C, existing walker wiring
       v
  PCA9685, unused for first motor test


                 Motor power domain

  3S LiPo, 11.1V nominal
       |
       +----> Left L298 +12V / VMS
       |
       +----> Right L298 +12V / VMS

  3S LiPo negative
       |
       +----> Left L298 GND
       |
       +----> Right L298 GND
       |
       +----> Raspberry Pi GND, physical pin 6
```

The shared ground is required so the L298 boards can understand the Pi's GPIO
signals. Only the grounds are tied together. Do not tie the 3S LiPo positive rail
to the Pi 5V rail.

## Motor Layout

Use one L298 board for the left side and one for the right side.

```text
Top view

        front

   left L298 board              right L298 board
   OUT1/OUT2 -> left front      OUT1/OUT2 -> right front
   OUT3/OUT4 -> left rear       OUT3/OUT4 -> right rear

        rear
```

Each L298 board has two channels. For first bring-up, both channels on the same
side are driven from the same three GPIO signals so the front and rear motors on
that side always move together.

## GPIO Mapping

BCM numbering is used here, not physical header numbering.

| Signal | Pi BCM | Pi physical pin | L298 connection |
|--------|--------|-----------------|-----------------|
| Left PWM | GPIO12 | pin 32 | Left ENA and ENB |
| Left forward | GPIO5 | pin 29 | Left IN1 and IN3 |
| Left reverse | GPIO6 | pin 31 | Left IN2 and IN4 |
| Right PWM | GPIO13 | pin 33 | Right ENA and ENB |
| Right forward | GPIO20 | pin 38 | Right IN1 and IN3 |
| Right reverse | GPIO21 | pin 40 | Right IN2 and IN4 |
| Ground | GND | pin 6 | Both L298 GND rails |

If the L298 boards have ENA/ENB jumpers installed, remove those jumpers so the Pi
can control speed with PWM. Then connect:

- Pi GPIO12 to both `ENA` and `ENB` on the left L298.
- Pi GPIO13 to both `ENA` and `ENB` on the right L298.

If a motor spins backward during testing, swap that motor's two output wires at
the L298 board. Keep the GPIO mapping unchanged.

## Six-wire Motor Leads

The JGA25-370 encoder motors have two heavy motor leads plus four encoder leads.
For the first motor test, only the motor leads connect to the L298 outputs.

Typical color mapping:

| Motor wire | First-test use | Notes |
|------------|----------------|-------|
| Red | L298 motor output | Usually motor positive |
| Black | L298 motor output | Usually motor negative |
| Yellow | leave disconnected | Encoder channel A on many JGA25 motors |
| Green | leave disconnected | Encoder channel B or encoder ground on some variants |
| Blue | leave disconnected | Encoder power or encoder signal on some variants |
| White | leave disconnected | Encoder power, ground, or signal on some variants |

For the motor side, yes: connect red and black to one L298 output pair such as
`OUT1` and `OUT2`. Direction is arbitrary at first. If the wheel spins backward,
swap red and black at that output pair.

Do not guess the encoder wiring from color alone before powering it. The four
encoder wires are low-current logic wires and should not be connected to L298
outputs or motor power.

## Optional PCA9685 PWM Wiring

The PCA9685 can provide PWM speed signals to the L298 `ENA` and `ENB` pins. Pi
GPIO would still provide the direction pins. This can make speed wiring tidier
later, but it does not remove the need to split battery power or pair motors to
the L298 output terminals.

```text
Pi I2C
  GPIO2 / physical pin 3  ----> PCA9685 SDA
  GPIO3 / physical pin 5  ----> PCA9685 SCL
  3.3V or 5V logic/VCC    ----> PCA9685 VCC, matching the existing board wiring
  GND / physical pin 6    ----> PCA9685 GND

PCA9685 PWM outputs
  channel 0 signal ----> Left L298 ENA and ENB
  channel 1 signal ----> Right L298 ENA and ENB
  PCA9685 GND      ----> Both L298 GND rails

Pi direction GPIO
  GPIO5  ----> Left L298 IN1 and IN3
  GPIO6  ----> Left L298 IN2 and IN4
  GPIO20 ----> Right L298 IN1 and IN3
  GPIO21 ----> Right L298 IN2 and IN4
```

This moves the PWM Y-splitters from the Pi header to the PCA9685 outputs:

- PCA9685 channel 0 signal still splits to left `ENA` and `ENB`.
- PCA9685 channel 1 signal still splits to right `ENA` and `ENB`.
- Direction wires still split because each side has two L298 channels.

So the PCA9685 helps if the Pi header is crowded or if all PWM should come from
one board, but it does not eliminate most Y-splitters in the first two-channel
skid-steer layout.

## L298 Board Power Notes

Most L298N modules have a `5V_EN` or `5V enable` jumper:

- With a 3S LiPo on the `+12V`/`VMS` terminal, the board usually powers its own
  5V logic regulator when the jumper is installed.
- Do not connect the L298 board's `5V` terminal to the Pi 5V pin during the first
  bring-up.
- If the exact L298 board requires an external 5V logic input, confirm that from
  the board silkscreen or listing before wiring the Pi 5V rail to it.

The Pi's 3.3V GPIO control signals are normally accepted by L298N input pins.

## Wiring Checklist

1. Power the Pi from the Waveshare UPS HAT only.
2. Leave the 3S LiPo disconnected while wiring GPIO.
3. Wire Pi GND pin 6 to both L298 `GND` terminals.
4. Wire the left board GPIO signals.
5. Wire the right board GPIO signals.
6. Wire the four motors to the L298 outputs.
7. Put the rover on blocks so the wheels cannot touch the table or floor.
8. Connect the 3S LiPo positive to both L298 `+12V`/`VMS` terminals.
9. Connect the 3S LiPo negative to both L298 `GND` terminals.
10. Run the motor test script at low duty cycle.

## First Test Goal

The first software goal is not driving the rover. It is only to prove:

1. Left side can spin forward.
2. Left side can spin reverse.
3. Right side can spin forward.
4. Right side can spin reverse.
5. Both sides can spin together at low PWM.

Start at 25% duty cycle for 1 second. If a side moves in the wrong direction,
swap that side's motor output wires or invert that side in software after both
motors on the side behave consistently.

## Minimal Test Script

Install `gpiozero` if it is not already present:

```bash
python3 -m pip install gpiozero
```

The repo includes [scripts/motor_test.py](../scripts/motor_test.py) with this
shape:

```python
from time import sleep

from gpiozero import Motor, PWMOutputDevice


class Side:
    def __init__(self, forward_pin, reverse_pin, enable_pin):
        self.motor = Motor(forward=forward_pin, backward=reverse_pin)
        self.enable = PWMOutputDevice(enable_pin)

    def forward(self, speed=0.25):
        self.enable.value = speed
        self.motor.forward()

    def reverse(self, speed=0.25):
        self.enable.value = speed
        self.motor.backward()

    def stop(self):
        self.motor.stop()
        self.enable.value = 0


left = Side(forward_pin=5, reverse_pin=6, enable_pin=12)
right = Side(forward_pin=20, reverse_pin=21, enable_pin=13)

try:
    print("left forward")
    left.forward()
    sleep(1)
    left.stop()
    sleep(1)

    print("left reverse")
    left.reverse()
    sleep(1)
    left.stop()
    sleep(1)

    print("right forward")
    right.forward()
    sleep(1)
    right.stop()
    sleep(1)

    print("right reverse")
    right.reverse()
    sleep(1)
    right.stop()
    sleep(1)

    print("both forward")
    left.forward()
    right.forward()
    sleep(1)
finally:
    left.stop()
    right.stop()
```

Run it only with the rover on blocks:

```bash
python3 scripts/motor_test.py
```

## Before the First Real Drive

- Add a physical motor-power switch or an easy XT60 disconnect.
- Strap the 3S LiPo down so it cannot hit the wheels.
- Check the LiPo voltage before and after the test.
- Keep the UPS HAT and Pi wiring physically away from the motor leads.
- Twist each motor's two output wires together to reduce electrical noise.
- Add strain relief to every motor wire before driving on the floor.
