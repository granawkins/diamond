#!/usr/bin/env python3
"""
Diamond Robot Web Controller
Simple FastAPI web app to control the Diamond quadruped robot over the local network.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import socket
import uvicorn

app = FastAPI(title="Diamond Robot Controller")

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
            max-width: 800px;
            margin: 50px auto;
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
        }
        .status {
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
        }
        .controls {
            margin-top: 30px;
            text-align: center;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Diamond Robot Controller</h1>
        <div class="status">
            <strong>Status:</strong> Connected<br>
            <small>Robot controls coming soon...</small>
        </div>
        <div class="controls">
            <button disabled>Forward</button>
            <button disabled>Backward</button>
            <button disabled>Turn Left</button>
            <button disabled>Turn Right</button>
            <button disabled>Reset</button>
        </div>
    </div>
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
