# Diamond

Diamond is a Raspberry Pi rover named after Neal Stephenson's *The Diamond Age*.
The current build is a four-motor, skid-steer rover in the `rover-v2` printed
body, controlled by an Xbox Wireless Controller.

The abandoned quadruped code and servo UI have been removed. The MG90/SG90 leg
approach was not strong enough once the battery and Pi hardware were installed,
so the project is now wheeled.

## Current Hardware

- Raspberry Pi powered from a Waveshare UPS HAT.
- Four DC gear motors, two on each side.
- Two L298 H-bridge boards, one per side.
- Separate Li-ion/LiPo motor battery with common ground to the Pi.
- Xbox Wireless Controller for live driving.
- `rover-v2` CAD files for the current 3D-printed body.

## Wiring

Do not power the motors from the Pi, UPS HAT, or GPIO header. The Pi and motors
use separate power domains with a shared ground.

```text
                 Brain power domain

  UPS HAT battery
       |
       v
  Waveshare UPS HAT
       |
       | 5V through HAT/header
       v
  Raspberry Pi


                 Motor power domain

  Motor battery positive
       |
       +----> Left L298 +12V / VMS
       |
       +----> Right L298 +12V / VMS

  Motor battery negative
       |
       +----> Left L298 GND
       |
       +----> Right L298 GND
       |
       +----> Raspberry Pi GND, physical pin 6
```

Only the grounds are tied together. Do not tie the motor battery positive rail to
the Pi 5V rail.

Use one L298 board for the left side and one for the right side.

```text
Top view

        front

   left L298 board              right L298 board
   OUT1/OUT2 -> left front      OUT1/OUT2 -> right front
   OUT3/OUT4 -> left rear       OUT3/OUT4 -> right rear

        rear
```

Each L298 board has two channels. Both channels on the same side are driven from
the same three GPIO signals so the front and rear motors on that side always move
together.

## GPIO

BCM numbering is used in code.

| Signal | Pi BCM | Pi physical pin | L298 connection |
|--------|--------|-----------------|-----------------|
| Left PWM | GPIO12 | pin 32 | Left ENA and ENB |
| Left forward | GPIO5 | pin 29 | Left IN1 and IN3 |
| Left reverse | GPIO6 | pin 31 | Left IN2 and IN4 |
| Right PWM | GPIO13 | pin 33 | Right ENA and ENB |
| Right forward | GPIO20 | pin 38 | Right IN1 and IN3 |
| Right reverse | GPIO16 | pin 36 | Right IN2 and IN4 |
| Ground | GND | pin 6 | Both L298 GND rails |

If the L298 boards have ENA/ENB jumpers installed, remove those jumpers so the Pi
can control speed with PWM. Then connect:

- Pi GPIO12 to both `ENA` and `ENB` on the left L298.
- Pi GPIO13 to both `ENA` and `ENB` on the right L298.

GPIO21 is reserved for I2S speaker audio and should not be used for motor
control.

## Speaker Audio

The MAX98357A I2S amplifier uses the Pi's standard I2S playback pins.

| MAX98357A | Pi BCM | Pi physical pin |
|-----------|--------|-----------------|
| BCLK | GPIO18 | pin 12 |
| LRC / LRCLK | GPIO19 | pin 35 |
| DIN | GPIO21 | pin 40 |
| VIN | 5V | pin 2 or 4 |
| GND | GND | any ground |

The runtime audio device is:

```text
plughw:CARD=MAX98357A,DEV=0
```

If a motor spins backward during testing, swap that motor's two output wires at
the L298 board. Keep the GPIO mapping unchanged.

## Motor Leads

Some gear motors include two heavy motor leads plus four encoder leads. For the
first motor test, only the motor leads connect to the L298 outputs.

Typical color mapping:

| Motor wire | First-test use | Notes |
|------------|----------------|-------|
| Red | L298 motor output | Usually motor positive |
| Black | L298 motor output | Usually motor negative |
| Yellow | leave disconnected | Encoder channel A on many motors |
| Green | leave disconnected | Encoder channel B or encoder ground on some variants |
| Blue | leave disconnected | Encoder power or encoder signal on some variants |
| White | leave disconnected | Encoder power, ground, or signal on some variants |

Do not guess the encoder wiring from color alone before powering it. The four
encoder wires are low-current logic wires and should not be connected to L298
outputs or motor power.

## L298 Power Notes

Most L298N modules have a `5V_EN` or `5V enable` jumper:

- With motor battery voltage on the `+12V`/`VMS` terminal, the board usually
  powers its own 5V logic regulator when the jumper is installed.
- Do not connect the L298 board's `5V` terminal to the Pi 5V pin during bring-up.
- If the exact L298 board requires an external 5V logic input, confirm that from
  the board silkscreen or listing before wiring the Pi 5V rail to it.

The Pi's 3.3V GPIO control signals are normally accepted by L298N input pins.

## Wiring Checklist

1. Power the Pi from the Waveshare UPS HAT only.
2. Leave the motor battery disconnected while wiring GPIO.
3. Wire Pi GND pin 6 to both L298 `GND` terminals.
4. Wire the left board GPIO signals.
5. Wire the right board GPIO signals.
6. Wire the four motors to the L298 outputs.
7. Put the rover on blocks so the wheels cannot touch the table or floor.
8. Connect motor battery positive to both L298 `+12V`/`VMS` terminals.
9. Connect motor battery negative to both L298 `GND` terminals.
10. Run `diamond.py` at a conservative speed and verify direction.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd webapp
npm install
```

## Web Control

The lightweight web page lives in [index.html](index.html) and is served by
[diamond.py](diamond.py). `diamond.py` is the single hardware owner and also
exposes HTTP endpoints for component testing.

```bash
.venv/bin/python diamond.py --max-speed 1.00
```

By default it listens on `0.0.0.0:3030`.

## Xbox Control

```bash
.venv/bin/python diamond.py --max-speed 1.00
```

The left stick maps to mixed drive: up/down is throttle, left/right is steering.
Put the rover on blocks for first tests. Use a lower `--max-speed` manually if
wiring or direction needs to be re-verified.

## Future Direction

Next major work is vision, audio input/output, and connecting the rover to an LLM,
probably through an API or over Tailscale to a local service running on a desktop
GPU.
