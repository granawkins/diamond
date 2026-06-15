import argparse
import subprocess
from pathlib import Path

from controllers.utils import capture_path


DEFAULT_CAMERA = 0
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_TIMEOUT_MS = 1000
DEFAULT_VIDEO_CODEC = "h264"


def default_image_path():
    return capture_path("image", "jpg")


def default_video_path(codec=DEFAULT_VIDEO_CODEC):
    extension = "h264" if codec == "h264" else codec
    return capture_path("video", extension)


def list_cameras():
    """Return rpicam's camera listing text."""

    result = subprocess.run(
        ["rpicam-still", "--list-cameras"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def capture_image(
    output_path,
    camera=DEFAULT_CAMERA,
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    timeout_ms=DEFAULT_TIMEOUT_MS,
):
    """Capture a still image from the Raspberry Pi camera."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "rpicam-still",
        "--camera",
        str(camera),
        "--width",
        str(int(width)),
        "--height",
        str(int(height)),
        "--timeout",
        str(int(timeout_ms)),
        "--output",
        str(output),
        "--nopreview",
    ]
    subprocess.run(command, check=True, timeout=(int(timeout_ms) / 1000) + 10)
    return output


def record_video(
    output_path,
    seconds=5,
    camera=DEFAULT_CAMERA,
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    codec=DEFAULT_VIDEO_CODEC,
):
    """Record video from the Raspberry Pi camera."""

    duration_ms = int(float(seconds) * 1000)
    if duration_ms <= 0:
        raise ValueError("seconds must be greater than 0")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "rpicam-vid",
        "--camera",
        str(camera),
        "--width",
        str(int(width)),
        "--height",
        str(int(height)),
        "--timeout",
        str(duration_ms),
        "--codec",
        codec,
        "--output",
        str(output),
        "--nopreview",
    ]
    subprocess.run(command, check=True, timeout=(duration_ms / 1000) + 10)
    return output


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Capture images or video from Diamond's Raspberry Pi camera. "
            "Import APIs: controllers.camera.capture_image(), record_video(), list_cameras()."
        )
    )
    parser.add_argument("output", nargs="?")
    parser.add_argument("--list", action="store_true", help="list detected cameras")
    parser.add_argument("--video", action="store_true", help="record video instead of a still image")
    parser.add_argument("--seconds", type=float, default=5, help="video duration")
    parser.add_argument("--camera", type=int, default=DEFAULT_CAMERA)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS, help="still capture warmup")
    parser.add_argument("--codec", default=DEFAULT_VIDEO_CODEC, help="video codec for rpicam-vid")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list:
        print(list_cameras())
        return

    if args.video:
        output_path = args.output or default_video_path(args.codec)
        output = record_video(
            output_path,
            seconds=args.seconds,
            camera=args.camera,
            width=args.width,
            height=args.height,
            codec=args.codec,
        )
        print(f"Recorded {args.seconds:g}s video to {output}")
    else:
        output_path = args.output or default_image_path()
        output = capture_image(
            output_path,
            camera=args.camera,
            width=args.width,
            height=args.height,
            timeout_ms=args.timeout_ms,
        )
        print(f"Captured image to {output}")


if __name__ == "__main__":
    main()
