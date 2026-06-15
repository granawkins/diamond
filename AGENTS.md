# Diamond

Diamond is a Raspberry Pi robot named after Neal Stephenson's *The Diamond Age*.
It's being created by Grant with the vision of being a companion / babysitter
for his baby son Lenny.

The project is currently two modules:
- A 'brain' built around a Raspberry Pi with a camera, led display, microphone 
  and speaker
- A 'rover' skid-steer base controlled by an Xbox controller.

## Project Structure

- `diamond.py` main control-loop entry point
- `controllers/` Python hardware controller modules
- `rover-v2*` CAD files for the current 3D-printed body
- `webapp/` Express-served control page
- `README.md` wiring and setup docs

## Python Controller Structure

Hardware-facing Python code belongs in `controllers/`. Each controller module
should be usable in two ways:

- Imported by `diamond.py` or future orchestration code through small exported
  functions/classes.
- Called directly from the CLI with `python -m controllers.<module> --help`.

Keep controller modules narrow and hardware-specific:

| Module | Responsibility |
|--------|----------------|
| `controllers/rover.py` | Skid-steer motor output and x/y drive mixing |
| `controllers/xbox_controller.py` | Xbox discovery, Bluetooth reconnect, event polling |
| `controllers/waveshare_hat.py` | Waveshare UPS HAT battery/current telemetry |
| `controllers/wifi.py` | Pi Wi-Fi signal level formatting |
| `controllers/led_display.py` | Dumb two-line LCD text output |
| `controllers/microphone.py` | USB microphone capture |
| `controllers/camera.py` | Raspberry Pi camera still/video capture |
| `controllers/speaker.py` | MAX98357A I2S speaker playback |
| `controllers/utils.py` | Shared controller utilities such as capture paths and optional-device retry |

Controller modules should fail gracefully at their boundary. If hardware may be
absent during boot or later reconnect, expose a connect/create function that
either returns a ready object or raises a clear exception. `diamond.py` should
use the shared optional controller retry helper instead of embedding per-device
retry state inline. Xbox input and rover motor output are both optional
controllers; drive commands are processed only when both are connected.

Generated media files go under `captures/`. The directory is gitignored except
for `captures/.gitkeep`; default filenames should use the shared timestamped
helpers in `controllers/utils.py`, e.g. `audio_<timestamp>.wav`.

## Hardware

### Brain
- Raspberry Pi 5
- Waveshare UPS HAT (B) circuit for Raspberry Pi, 5V 5A, Pogo Pins Connector
- MKE-M07 LCD1602 I2C Module Display
- USB 2.0 mini microphone
- Raspberry Pi Camera Module 3 Wide, 120-degree
- MAX98357A I2S Audio Amplifier
- Mini 3W 8 ohm speaker with plastic casing

### Rover
- Xbox Wireless Controller MAC: `40:8E:2C:4A:2D:2E`.
- M609 low-voltage measurement/protection module
- Lithium Ion 3C 2200 mAH battery
- Two L298 H-bridges, one per side.
- Four DC Servo JGA25-370 gear motors with wheels

GPIO uses BCM numbering:

| Side | Forward | Reverse | Enable PWM |
|------|---------|---------|------------|
| Left | GPIO5 | GPIO6 | GPIO12 |
| Right | GPIO20 | GPIO16 | GPIO13 |

MAX98357A I2S speaker wiring uses the Pi's standard I2S playback pins:

| MAX98357A | Pi GPIO | Pi physical pin |
|-----------|---------|-----------------|
| BCLK | GPIO18 | pin 12 |
| LRC / LRCLK | GPIO19 | pin 35 |
| DIN | GPIO21 | pin 40 |
| VIN | 5V | pin 2 or 4 |
| GND | GND | any ground |

GPIO21 is reserved for I2S audio data and should not be reused for rover motor
control.

### Still Need

- Stranded copper silicone wire:
  - 16-18 AWG for battery/H-bridge/motor power
  - 22-24 AWG for signal/jumper harnesses
- Inline automotive blade fuse holder
- Blade fuse assortment: 5A, 7.5A, 10A
- Heat shrink tubing assortment
- Ferrule crimper kit with assorted ferrules
- Terminal block or Wago-style lever connectors for splitting motor battery
  power to the two H-bridges
- Zip ties or cable clamps for strain relief

## Webapp

The web page lives in `webapp/` and is served by the Express server in
`webapp/server.js`. It is a lightweight status page only; do not add pulse/mix
motor controls back unless the user asks.

Start it from the repository root with:

```bash
cd webapp
npm start
```

The server listens on `0.0.0.0:3030`, so it is reachable from the user's desktop
over Tailscale at:

```text
http://100.71.9.108:3030/
```

If a sandboxed start fails with `listen EPERM: operation not permitted
0.0.0.0:3030`, rerun the same `npm start` command with elevated permissions.

## Xbox Rover Drive

The currently paired/trusted Xbox Wireless Controller creates `/dev/input/event5`,
`/dev/input/event6`, `/dev/input/event7`, and `/dev/input/js0` when connected.

The live Xbox controller rover driver is:

```bash
.venv/bin/python diamond.py --max-speed 1.00
```

It reads the Xbox left stick from `/dev/input/event5` by default, but validates
that the event device exposes the expected stick axes and falls back to an Xbox
device scan if needed. The left stick maps up/down to throttle and left/right to
steering; stick release centers both axes and stops the motors.

The main loop is expected to keep running when optional hardware is missing. LCD
status should continue updating if the Xbox controller or motor GPIO is
unavailable; drive commands should only be sent to motors when both the Xbox
controller and real rover motor output are present.

Run the rover on blocks for first tests. Use a conservative manual `--max-speed`
such as `0.25` or `0.40` when wiring and direction need to be re-verified.
