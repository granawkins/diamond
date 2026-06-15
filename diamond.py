import argparse
import asyncio
import subprocess
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from time import monotonic

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from controllers.camera import capture_image, default_image_path, record_video
from controllers.led_display import LedDisplay
from controllers.microphone import (
    DEFAULT_CHANNELS as MIC_CHANNELS,
    DEFAULT_CONTAINER as MIC_CONTAINER,
    DEFAULT_DEVICE as MIC_DEVICE,
    DEFAULT_FORMAT as MIC_FORMAT,
    DEFAULT_RATE as MIC_RATE,
    default_audio_path,
)
from controllers.rover import connect_rover
from controllers.speaker import play_file, play_tone
from controllers.utils import CAPTURE_DIR, OptionalController, capture_path
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
WEB_DRIVE_TIMEOUT = 0.4
PORT = 3030
INDEX_FILE = Path(__file__).resolve().parent / "index.html"


class DisplayMessage(BaseModel):
    text: str = Field(default="", max_length=64)


class DriveCommand(BaseModel):
    x: float = Field(ge=-1, le=1)
    y: float = Field(ge=-1, le=1)


class ToneRequest(BaseModel):
    frequency: int = Field(default=660, ge=80, le=4000)
    seconds: float = Field(default=0.15, gt=0, le=3)
    volume: float = Field(default=0.05, ge=0, le=1)


class CaptureName(BaseModel):
    name: str


class TimedCapture(BaseModel):
    seconds: float = Field(default=3, gt=0, le=30)


class AppState:
    def __init__(self, args):
        self.args = args
        self.rover = OptionalController(
            "Rover motor output",
            lambda: connect_rover(max_speed=args.max_speed),
            retry_interval=CONTROLLER_RETRY_INTERVAL,
        )
        self.xbox = OptionalController(
            "Xbox controller",
            lambda: connect_xbox_controller(
                device_path=args.device,
                controller_mac=args.controller_mac,
                deadzone=args.deadzone,
            ),
            retry_interval=CONTROLLER_RETRY_INTERVAL,
        )
        self.display = None
        self.message = args.message
        self.web_drive = None
        self.web_drive_at = 0
        self.battery = None
        self.wifi = None
        self.mic_process = None
        self.mic_output = None
        self.running = True
        self.hardware_task = None


def parse_args():
    parser = argparse.ArgumentParser(description="Run Diamond's FastAPI hardware server.")
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    parser.add_argument("--controller-mac", default=DEFAULT_CONTROLLER_MAC)
    parser.add_argument("--deadzone", type=float, default=0.08)
    parser.add_argument("--max-speed", type=float, default=1.00)
    parser.add_argument("--message", default="Diamond online")
    parser.add_argument("--no-display", action="store_true")
    parser.add_argument("--wifi-interface", help="wireless interface to read, such as wlan0")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=PORT)
    return parser.parse_args()


def status_line(battery, wifi):
    battery_text = f"BAT {battery['percent']:.0f}%" if battery else "BAT --%"
    return f"{battery_text} {format_wifi_level(wifi)}"[:16]


def update_display(state):
    try:
        state.battery = read_battery()
    except OSError as error:
        print(f"Battery read failed: {error}", flush=True)
        state.battery = None

    state.wifi = read_wifi_level(state.args.wifi_interface)

    if state.display:
        state.display.write(status_line(state.battery, state.wifi), state.message)


async def hardware_loop(state):
    if not state.args.no_display:
        try:
            state.display = LedDisplay()
            await asyncio.to_thread(update_display, state)
        except OSError as error:
            print(f"Display unavailable: {error}", flush=True)
            state.display = None

    next_display_update = monotonic() + DISPLAY_INTERVAL
    stopped = True

    while state.running:
        now = monotonic()
        controller = await asyncio.to_thread(state.xbox.tick, now)
        motor_output = await asyncio.to_thread(state.rover.tick, now)
        xbox_state = None

        if controller is not None:
            try:
                xbox_state = controller.poll(timeout=0)
            except OSError as error:
                state.xbox.clear(error)
                stop_rover(state)

        drive_command = None
        if state.web_drive and now - state.web_drive_at <= WEB_DRIVE_TIMEOUT:
            drive_command = state.web_drive
        elif xbox_state is not None:
            drive_command = {"x": xbox_state.x, "y": xbox_state.y}

        if motor_output is not None and drive_command is not None:
            motor_output.drive(drive_command["x"], drive_command["y"])
            stopped = False
        elif not stopped:
            stop_rover(state)
            stopped = True

        if now >= next_display_update:
            try:
                await asyncio.to_thread(update_display, state)
            except OSError as error:
                print(f"Display update failed: {error}", flush=True)
                state.display = None
            next_display_update = now + DISPLAY_INTERVAL

        await asyncio.sleep(DRIVE_POLL_INTERVAL)


def stop_rover(state):
    if state.rover.device:
        state.rover.device.stop()


def capture_file(name):
    path = (CAPTURE_DIR / name).resolve()
    capture_root = CAPTURE_DIR.resolve()

    if capture_root not in path.parents:
        raise HTTPException(status_code=400, detail="Invalid capture path")

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Capture not found")

    return path


def list_captures():
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    captures = []

    for path in sorted(CAPTURE_DIR.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        if path.suffix.lower() == ".h264":
            continue

        captures.append(
            {
                "name": path.name,
                "size": path.stat().st_size,
                "url": f"/captures/{path.name}",
                "kind": capture_kind(path),
            }
        )

    return captures


def capture_kind(path):
    suffix = path.suffix.lower()
    if suffix in (".jpg", ".jpeg", ".png"):
        return "image"
    if suffix in (".mp4", ".webm"):
        return "video"
    if suffix in (".wav", ".raw", ".mp3"):
        return "audio"
    return "file"


def start_microphone_recording(state):
    if state.mic_process and state.mic_process.poll() is None:
        raise HTTPException(status_code=409, detail="Recording already in progress")

    output = default_audio_path("wav")
    command = [
        "arecord",
        "-D",
        MIC_DEVICE,
        "-f",
        MIC_FORMAT,
        "-r",
        str(MIC_RATE),
        "-c",
        str(MIC_CHANNELS),
        "-t",
        MIC_CONTAINER,
        str(output),
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    state.mic_process = subprocess.Popen(command)
    state.mic_output = output
    return output


def stop_microphone_recording(state):
    if not state.mic_process:
        raise HTTPException(status_code=409, detail="Recording is not running")

    process = state.mic_process
    output = state.mic_output

    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)

    state.mic_process = None
    state.mic_output = None
    return output


def record_mp4(seconds):
    mp4_output = capture_path("video", "mp4")

    with tempfile.NamedTemporaryFile(prefix="diamond-video-", suffix=".h264", delete=True) as file:
        raw_output = Path(file.name)
        record_video(raw_output, seconds=seconds)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw_output), "-c", "copy", str(mp4_output)],
            check=True,
            timeout=float(seconds) + 15,
        )

    return mp4_output


def create_app(args=None):
    args = args or parse_args()
    state = AppState(args)

    @asynccontextmanager
    async def lifespan(app):
        app.state.diamond = state
        state.hardware_task = asyncio.create_task(hardware_loop(state))
        try:
            yield
        finally:
            state.running = False
            if state.hardware_task:
                state.hardware_task.cancel()
            stop_rover(state)
            if state.display:
                state.display.close()
            if state.mic_process and state.mic_process.poll() is None:
                state.mic_process.terminate()

    app = FastAPI(title="Diamond Rover", lifespan=lifespan)
    app.mount("/captures", StaticFiles(directory=CAPTURE_DIR), name="captures")

    @app.get("/")
    def index():
        return FileResponse(INDEX_FILE)

    @app.get("/api/status")
    def api_status():
        return {
            "battery": state.battery,
            "wifi": state.wifi,
            "display": {"message": state.message},
            "controllers": {
                "rover": state.rover.available,
                "xbox": state.xbox.available,
                "display": state.display is not None,
                "mic_recording": state.mic_process is not None and state.mic_process.poll() is None,
            },
            "captures": list_captures(),
        }

    @app.post("/api/display/message")
    def api_display_message(payload: DisplayMessage):
        state.message = payload.text
        if state.display:
            state.display.write_line(1, state.message)
        return {"ok": True, "message": state.message}

    @app.post("/api/drive")
    def api_drive(payload: DriveCommand):
        state.web_drive = {"x": payload.x, "y": payload.y}
        state.web_drive_at = monotonic()
        return {"ok": True}

    @app.post("/api/drive/stop")
    def api_drive_stop():
        state.web_drive = None
        stop_rover(state)
        return {"ok": True}

    @app.post("/api/mic/record/start")
    def api_mic_start():
        output = start_microphone_recording(state)
        return {"ok": True, "capture": output.name}

    @app.post("/api/mic/record/stop")
    def api_mic_stop():
        output = stop_microphone_recording(state)
        return {"ok": True, "capture": output.name if output else None}

    @app.post("/api/speaker/tone")
    async def api_speaker_tone(payload: ToneRequest):
        await asyncio.to_thread(
            play_tone,
            frequency=payload.frequency,
            seconds=payload.seconds,
            volume=payload.volume,
        )
        return {"ok": True}

    @app.post("/api/speaker/play")
    async def api_speaker_play(payload: CaptureName):
        path = capture_file(payload.name)
        await asyncio.to_thread(play_file, path)
        return {"ok": True}

    @app.post("/api/camera/photo")
    async def api_camera_photo():
        output = await asyncio.to_thread(capture_image, default_image_path())
        return {"ok": True, "capture": output.name}

    @app.post("/api/camera/video")
    async def api_camera_video(payload: TimedCapture):
        output = await asyncio.to_thread(record_mp4, payload.seconds)
        return {"ok": True, "capture": output.name}

    @app.get("/api/captures")
    def api_captures():
        return {"captures": list_captures()}

    return app


def main():
    args = parse_args()
    uvicorn.run(create_app(args), host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
