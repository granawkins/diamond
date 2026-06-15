import argparse
import math
import subprocess
from pathlib import Path

from controllers.utils import capture_path


DEFAULT_DEVICE = "plughw:CARD=Device,DEV=0"
DEFAULT_RATE = 16000
DEFAULT_CHANNELS = 1
DEFAULT_FORMAT = "S16_LE"
DEFAULT_CONTAINER = "wav"


def default_audio_path(container=DEFAULT_CONTAINER):
    extension = "raw" if container == "raw" else "wav"
    return capture_path("audio", extension)


def list_microphones():
    """Return ALSA capture device listing text from arecord."""

    result = subprocess.run(
        ["arecord", "-l"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def record_audio(
    output_path,
    seconds=3,
    device=DEFAULT_DEVICE,
    rate=DEFAULT_RATE,
    channels=DEFAULT_CHANNELS,
    sample_format=DEFAULT_FORMAT,
    container=DEFAULT_CONTAINER,
):
    """Record audio from the USB microphone to a WAV or raw PCM file."""

    duration = int(math.ceil(float(seconds)))
    if duration <= 0:
        raise ValueError("seconds must be greater than 0")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "arecord",
        "-D",
        device,
        "-f",
        sample_format,
        "-r",
        str(int(rate)),
        "-c",
        str(int(channels)),
        "-d",
        str(duration),
        "-t",
        container,
        str(output),
    ]

    subprocess.run(command, check=True, timeout=duration + 5)
    return output


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Record audio from Diamond's USB microphone. "
            "Import API: controllers.microphone.record_audio(output_path, seconds=3)."
        )
    )
    parser.add_argument("output", nargs="?")
    parser.add_argument("--seconds", type=float, default=3)
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    parser.add_argument("--rate", type=int, default=DEFAULT_RATE)
    parser.add_argument("--channels", type=int, default=DEFAULT_CHANNELS)
    parser.add_argument("--format", default=DEFAULT_FORMAT)
    parser.add_argument(
        "--container",
        default=DEFAULT_CONTAINER,
        choices=("wav", "raw"),
        help="wav adds a header; raw writes headerless PCM samples",
    )
    parser.add_argument("--list", action="store_true", help="list ALSA capture devices")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list:
        print(list_microphones())
        return

    output_path = args.output or default_audio_path(args.container)
    output = record_audio(
        output_path,
        seconds=args.seconds,
        device=args.device,
        rate=args.rate,
        channels=args.channels,
        sample_format=args.format,
        container=args.container,
    )
    print(f"Recorded {args.seconds:g}s to {output}")


if __name__ == "__main__":
    main()
