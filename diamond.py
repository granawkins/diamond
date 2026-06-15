import argparse
from time import monotonic, sleep

from controllers.led_display import LedDisplay
from controllers.rover import connect_rover
from controllers.utils import OptionalController
from controllers.waveshare_hat import read_battery
from controllers.wifi import format_wifi_level, read_wifi_level
from controllers.xbox_controller import (
    DEFAULT_CONTROLLER_MAC,
    DEFAULT_DEVICE,
    connect_xbox_controller,
)


DISPLAY_INTERVAL = 1.0
DRIVE_POLL_INTERVAL = 0.05
CONTROLLER_RETRY_INTERVAL = 5.0


def parse_args():
    parser = argparse.ArgumentParser(description="Run Diamond's rover control loop.")
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    parser.add_argument("--controller-mac", default=DEFAULT_CONTROLLER_MAC)
    parser.add_argument("--deadzone", type=float, default=0.08)
    parser.add_argument("--max-speed", type=float, default=1.00)
    parser.add_argument("--message", default="Diamond online")
    parser.add_argument("--no-display", action="store_true")
    parser.add_argument("--wifi-interface", help="wireless interface to read, such as wlan0")
    return parser.parse_args()


def status_line(battery, wifi):
    battery_text = f"BAT {battery['percent']:.0f}%" if battery else "BAT --%"
    return f"{battery_text} {format_wifi_level(wifi)}"[:16]


def update_display(display, message, wifi_interface):
    try:
        battery = read_battery()
    except OSError as error:
        print(f"Battery read failed: {error}", flush=True)
        battery = None

    wifi = read_wifi_level(wifi_interface)
    line1 = status_line(battery, wifi)
    display.write(line1, message)
    return line1


def main():
    args = parse_args()
    rover = OptionalController(
        "Rover motor output",
        lambda: connect_rover(max_speed=args.max_speed),
        retry_interval=CONTROLLER_RETRY_INTERVAL,
    )
    xbox = OptionalController(
        "Xbox controller",
        lambda: connect_xbox_controller(
            device_path=args.device,
            controller_mac=args.controller_mac,
            deadzone=args.deadzone,
        ),
        retry_interval=CONTROLLER_RETRY_INTERVAL,
    )
    display = None

    print("Diamond control loop starting. Press Ctrl+C to exit.")

    try:
        if not args.no_display:
            try:
                display = LedDisplay()
                update_display(display, args.message, args.wifi_interface)
            except OSError as error:
                print(f"Display unavailable: {error}", flush=True)
                display = None

        next_display_update = monotonic() + DISPLAY_INTERVAL

        while True:
            now = monotonic()
            controller = xbox.tick(now)
            motor_output = rover.tick(now)

            if controller is None:
                sleep(DRIVE_POLL_INTERVAL)
            else:
                try:
                    state = controller.poll(timeout=DRIVE_POLL_INTERVAL)
                except OSError as error:
                    xbox.clear(error)
                    stop_rover(rover)
                    continue

                if state.changed and motor_output is not None:
                    powers = motor_output.drive(state.x, state.y)
                    print_drive_state(state, powers)

            now = monotonic()

            if display and now >= next_display_update:
                try:
                    update_display(display, args.message, args.wifi_interface)
                except OSError as error:
                    print(f"Display update failed: {error}", flush=True)
                    display = None
                next_display_update = now + DISPLAY_INTERVAL

    except KeyboardInterrupt:
        print("Stopping")
    finally:
        stop_rover(rover)
        if display:
            display.close()
        sleep(0.05)


def stop_rover(rover):
    if rover.device:
        rover.device.stop()


def print_drive_state(state, powers):
    print(
        f"x={state.x:+.0%} y={state.y:+.0%} "
        f"left={powers['left']:+.0%} right={powers['right']:+.0%}",
        flush=True,
    )


if __name__ == "__main__":
    main()
