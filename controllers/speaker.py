import argparse
import math
import tempfile
import subprocess
import wave
from pathlib import Path


"""
Persistent Raspberry Pi setup for the MAX98357A I2S amplifier lives in
/boot/firmware/config.txt:

    dtparam=i2s=on
    dtoverlay=max98357a

After changing those lines, reboot before relying on the speaker after startup.
"""

DEFAULT_DEVICE = "plughw:CARD=MAX98357A,DEV=0"
DEFAULT_FREQUENCY = 880
DEFAULT_SECONDS = 0.25
DEFAULT_VOLUME = 0.10
DEFAULT_RATE = 48000


def list_speakers():
    """Return ALSA playback device listing text from aplay."""

    result = subprocess.run(
        ["aplay", "-l"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def play_file(path, device=DEFAULT_DEVICE):
    """Play an audio file through the MAX98357A speaker output."""

    audio_path = Path(path)
    subprocess.run(["aplay", "-D", device, str(audio_path)], check=True)


def clamp(value, minimum=0, maximum=1):
    return max(minimum, min(maximum, value))


def write_tone(path, frequency=DEFAULT_FREQUENCY, seconds=DEFAULT_SECONDS, volume=DEFAULT_VOLUME):
    duration = float(seconds)
    if duration <= 0:
        raise ValueError("seconds must be greater than 0")

    amplitude = int(32767 * clamp(float(volume)))
    frames = int(DEFAULT_RATE * duration)

    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(DEFAULT_RATE)

        for index in range(frames):
            sample = int(amplitude * math.sin(2 * math.pi * frequency * index / DEFAULT_RATE))
            output.writeframesraw(sample.to_bytes(2, "little", signed=True))


def play_tone(
    frequency=DEFAULT_FREQUENCY,
    seconds=DEFAULT_SECONDS,
    volume=DEFAULT_VOLUME,
    device=DEFAULT_DEVICE,
):
    """Play a short sine tone through the MAX98357A speaker output."""

    with tempfile.NamedTemporaryFile(prefix="diamond-tone-", suffix=".wav", delete=True) as file:
        write_tone(file.name, frequency=frequency, seconds=seconds, volume=volume)
        play_file(file.name, device=device)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Play audio through Diamond's MAX98357A I2S speaker. "
            "Import APIs: controllers.speaker.play_file(), play_tone(), list_speakers()."
        )
    )
    parser.add_argument("file", nargs="?", help="audio file to play with aplay")
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    parser.add_argument("--list", action="store_true", help="list ALSA playback devices")
    parser.add_argument("--tone", action="store_true", help="play a sine tone instead of a file")
    parser.add_argument("--frequency", type=int, default=DEFAULT_FREQUENCY)
    parser.add_argument("--seconds", type=float, default=DEFAULT_SECONDS)
    parser.add_argument("--volume", type=float, default=DEFAULT_VOLUME, help="0.0 to 1.0")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list:
        print(list_speakers())
    elif args.tone or not args.file:
        play_tone(
            frequency=args.frequency,
            seconds=args.seconds,
            volume=args.volume,
            device=args.device,
        )
    else:
        play_file(args.file, device=args.device)


if __name__ == "__main__":
    main()
