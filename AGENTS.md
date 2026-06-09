# AGENTS.md

Guidance for agents working in this repository.

## Motor Pulse Webapp

The motor pulse controls page lives in `webapp/` and is served by the Express
server in `webapp/server.js`.

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

The currently paired/trusted Xbox Wireless Controller MAC is
`40:8E:2C:4A:2D:2E`. It creates `/dev/input/event5`, `/dev/input/event6`,
`/dev/input/event7`, and `/dev/input/js0` when connected.

The live Xbox controller rover driver is:

```bash
.venv/bin/python scripts/xbox_rover_drive.py --max-speed 0.40
```

It reads the Xbox left stick from `/dev/input/event5` by default, falling back to
an Xbox device scan if that path no longer exists. The left stick maps like the
webapp's Mixed Drive pad: up/down is throttle, left/right is steering, and stick
release centers both axes and stops the motors.

Run the rover on blocks for first tests. Use a conservative `--max-speed` such as
`0.25` or `0.40` until wiring and direction are verified.
