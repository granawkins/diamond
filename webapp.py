#!/usr/bin/env python3
"""
Diamond Robot Web Controller
Simple FastAPI web app to control the Diamond quadruped robot over the local network.
"""

from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import socket
import uvicorn
from typing import Dict, Optional
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_ina219 import INA219

app = FastAPI(title="Diamond Robot Controller")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
templates = Jinja2Templates(directory="webapp/templates")

# Initialize hardware
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50

    # Create servo objects for all 16 channels
    servos = {}
    for i in range(16):
        # Skip empty channels
        if i not in [3, 7, 11, 15]:
            servos[i] = servo.Servo(pca.channels[i], min_pulse=500, max_pulse=2500)

    # Initialize INA219 for battery monitoring
    try:
        ina219 = INA219(i2c)
        battery_monitor_available = True
        print("✓ Battery monitor initialized successfully")
    except Exception as bat_err:
        battery_monitor_available = False
        ina219 = None
        print(f"⚠ Battery monitor not available: {bat_err}")

    hardware_available = True
    print("✓ Hardware initialized successfully")
except Exception as e:
    hardware_available = False
    battery_monitor_available = False
    servos = {}
    ina219 = None
    print(f"⚠ Hardware not available: {e}")
    print("  Running in simulation mode")

# Servo channel names
SERVO_NAMES = {
    0: "Front Left - Lower Hip",
    1: "Front Left - Upper Hip",
    2: "Front Left - Shoulder",
    3: "Front Left - (empty)",
    4: "Back Left - Lower Hip",
    5: "Back Left - Upper Hip",
    6: "Back Left - Shoulder",
    7: "Back Left - (empty)",
    8: "Back Right - Lower Hip",
    9: "Back Right - Upper Hip",
    10: "Back Right - Shoulder",
    11: "Back Right - (empty)",
    12: "Front Right - Lower Hip",
    13: "Front Right - Upper Hip",
    14: "Front Right - Shoulder",
    15: "Front Right - (empty)",
}

# Store current servo positions
servo_positions: Dict[int, int] = {i: 90 for i in range(16)}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main control page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def status():
    """Return robot status"""
    return {"status": "ready", "message": "Diamond robot is ready"}

@app.get("/api/battery")
async def battery_status():
    """Return battery status from INA219"""
    if not battery_monitor_available or ina219 is None:
        return {
            "available": False,
            "voltage": 0,
            "current": 0,
            "power": 0,
            "status": "unavailable"
        }

    try:
        bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
        shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V-
        current_ma = ina219.current  # current in mA
        power_mw = ina219.power  # power in mW

        # Total voltage is bus + shunt
        voltage = bus_voltage + (shunt_voltage / 1000)
        current_a = current_ma / 1000
        power_w = power_mw / 1000

        # Determine charging/discharging status
        if current_a < -0.05:  # Negative = discharging
            status = "discharging"
        elif current_a > 0.05:  # Positive = charging
            status = "charging"
        else:
            status = "idle"

        return {
            "available": True,
            "voltage": round(voltage, 2),
            "current": round(current_a, 3),
            "power": round(power_w, 2),
            "status": status
        }
    except Exception as e:
        print(f"✗ Error reading battery status: {e}")
        return {
            "available": False,
            "voltage": 0,
            "current": 0,
            "power": 0,
            "status": "error",
            "error": str(e)
        }

@app.post("/api/servo")
async def set_servo(data: Dict = Body(...)):
    """Set servo position for a specific channel"""
    channel = data.get("channel")
    angle = data.get("angle")

    if channel is None or angle is None:
        return {"error": "Missing channel or angle"}, 400

    if not (0 <= channel <= 15):
        return {"error": "Channel must be between 0 and 15"}, 400

    if not (0 <= angle <= 180):
        return {"error": "Angle must be between 0 and 180"}, 400

    # Store the position
    servo_positions[channel] = angle

    # Control the actual servo if hardware is available
    if hardware_available and channel in servos:
        try:
            servos[channel].angle = angle
            print(f"✓ Servo {channel} ({SERVO_NAMES[channel]}) set to {angle}°")
        except Exception as e:
            print(f"✗ Error setting servo {channel}: {e}")
            return {"error": f"Failed to set servo: {e}"}, 500
    else:
        print(f"⚠ Simulation: Servo {channel} ({SERVO_NAMES[channel]}) → {angle}°")

    return {
        "success": True,
        "channel": channel,
        "angle": angle,
        "name": SERVO_NAMES[channel],
        "hardware": hardware_available
    }

def get_local_ip():
    """Get the local IP address of the Pi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    ip = get_local_ip()
    port = 8000
    print(f"\n🤖 Diamond Robot Web Controller")
    print(f"=" * 50)
    print(f"Access from your desktop at: http://{ip}:{port}")
    print(f"=" * 50)
    print(f"\nPress Ctrl+C to stop the server\n")

    uvicorn.run("webapp:app", host='0.0.0.0', port=port, reload=True)
