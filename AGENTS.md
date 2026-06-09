# AGENTS.md

Guidance for agents working in this repository.

## Project Shape

Diamond is currently a Raspberry Pi rover, not a quadruped. Keep the repo focused
on:

- `diamond_rover/` shared Python rover-control helpers
- `diamond.py` Xbox driving entry point
- `webapp/` Express-served control page
- `README.md` wiring and setup docs
- `rover-v2*` CAD files for the current 3D-printed body

The old SG90/MG90 quadruped code and Claude-specific instructions were removed.
Do not reintroduce walker/leg/kinematics/PCA9685 servo control unless the user
explicitly asks for that path again.

## Hardware

- Raspberry Pi powered from a Waveshare UPS HAT.
- Four DC gear motors.
- Two L298 H-bridges, one per side.
- Separate motor battery with common ground to the Pi.
- Xbox Wireless Controller MAC: `40:8E:2C:4A:2D:2E`.

GPIO uses BCM numbering:

| Side | Forward | Reverse | Enable PWM |
|------|---------|---------|------------|
| Left | GPIO5 | GPIO6 | GPIO12 |
| Right | GPIO20 | GPIO21 | GPIO13 |

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

It reads the Xbox left stick from `/dev/input/event5` by default, falling back to
an Xbox device scan if that path no longer exists. The left stick maps up/down to
throttle and left/right to steering; stick release centers both axes and stops
the motors.

Run the rover on blocks for first tests. Use a conservative manual `--max-speed`
such as `0.25` or `0.40` when wiring and direction need to be re-verified.
