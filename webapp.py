#!/usr/bin/env python3
"""
Diamond Robot Web Controller
Simple FastAPI web app to control the Diamond quadruped robot over the local network.
"""

from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
import socket
import uvicorn
from typing import Dict, Optional
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

app = FastAPI(title="Diamond Robot Controller")

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

    hardware_available = True
    print("✓ Hardware initialized successfully")
except Exception as e:
    hardware_available = False
    servos = {}
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

# HTML template for the control page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diamond Robot Controller</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 20px auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .servo-row {
            display: grid;
            grid-template-columns: 60px 250px 1fr 60px;
            gap: 15px;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            background-color: #f9f9f9;
            border-radius: 5px;
            transition: background-color 0.2s;
        }
        .servo-row:hover {
            background-color: #f0f0f0;
        }
        .channel {
            font-weight: bold;
            color: #666;
            text-align: center;
        }
        .name {
            color: #333;
            font-size: 14px;
        }
        .slider {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            outline: none;
            -webkit-appearance: none;
            background: #ddd;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #4CAF50;
            cursor: pointer;
        }
        .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #4CAF50;
            cursor: pointer;
            border: none;
        }
        .value {
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            min-width: 40px;
        }
        .empty {
            opacity: 0.4;
        }
        .empty .slider {
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Diamond Servo Controller</h1>
        <div id="servos"></div>
    </div>

    <script>
        const servoNames = {
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
            15: "Front Right - (empty)"
        };

        const servosContainer = document.getElementById('servos');

        // Create servo controls
        for (let i = 0; i < 16; i++) {
            const row = document.createElement('div');
            row.className = 'servo-row' + (servoNames[i].includes('empty') ? ' empty' : '');

            const channel = document.createElement('div');
            channel.className = 'channel';
            channel.textContent = `CH ${i}`;

            const name = document.createElement('div');
            name.className = 'name';
            name.textContent = servoNames[i];

            const slider = document.createElement('input');
            slider.type = 'range';
            slider.min = 0;
            slider.max = 180;
            slider.value = 90;
            slider.className = 'slider';
            slider.id = `servo-${i}`;

            const value = document.createElement('div');
            value.className = 'value';
            value.textContent = '90°';
            value.id = `value-${i}`;

            // Add event listener for real-time updates
            slider.addEventListener('input', function() {
                value.textContent = this.value + '°';
            });

            slider.addEventListener('change', async function() {
                const channel = i;
                const angle = parseInt(this.value);

                try {
                    const response = await fetch('/api/servo', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ channel, angle })
                    });

                    if (!response.ok) {
                        console.error('Failed to set servo position');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });

            row.appendChild(channel);
            row.appendChild(name);
            row.appendChild(slider);
            row.appendChild(value);
            servosContainer.appendChild(row);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main control page"""
    return HTML_TEMPLATE

@app.get("/api/status")
async def status():
    """Return robot status"""
    return {"status": "ready", "message": "Diamond robot is ready"}

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

    uvicorn.run(app, host='0.0.0.0', port=port)
