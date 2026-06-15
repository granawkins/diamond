import argparse
import os


DEFAULT_WIRELESS_PATH = "/proc/net/wireless"


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def wifi_bars(percent):
    if percent is None:
        return 0
    if percent >= 75:
        return 4
    if percent >= 50:
        return 3
    if percent >= 25:
        return 2
    if percent > 0:
        return 1
    return 0


def read_wifi_level(interface=None, wireless_path=DEFAULT_WIRELESS_PATH):
    """Read Pi Wi-Fi signal from /proc/net/wireless."""

    if not os.path.exists(wireless_path):
        return {"interface": interface, "quality": None, "level": None, "noise": None, "bars": 0}

    with open(wireless_path, encoding="utf-8") as file:
        rows = file.readlines()[2:]

    for row in rows:
        if ":" not in row:
            continue

        name, values = row.split(":", 1)
        name = name.strip()

        if interface and name != interface:
            continue

        fields = values.split()
        if len(fields) < 4:
            continue

        quality = float(fields[1].strip("."))
        level = float(fields[2].strip("."))
        noise = float(fields[3].strip("."))
        percent = clamp((quality / 70) * 100)

        return {
            "interface": name,
            "quality": percent,
            "level": level,
            "noise": noise,
            "bars": wifi_bars(percent),
        }

    return {"interface": interface, "quality": None, "level": None, "noise": None, "bars": 0}


def format_wifi_level(signal):
    if signal["quality"] is None:
        return "WIFI 0/4"

    return f"WIFI {signal['bars']}/4"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Read Diamond's Pi Wi-Fi signal. "
            "Import API: controllers.wifi.read_wifi_level() returns a dict."
        )
    )
    parser.add_argument("--interface", help="wireless interface to read, such as wlan0")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    return parser.parse_args()


def main():
    args = parse_args()
    signal = read_wifi_level(args.interface)

    if args.json:
        import json

        print(json.dumps(signal, sort_keys=True))
    else:
        print(format_wifi_level(signal))


if __name__ == "__main__":
    main()

