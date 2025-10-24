from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn
from controllers.servo import CHANNEL_TO_NAME, SERVO_CONFIG

app = FastAPI()
app.mount("/static", StaticFiles(directory="subscribers/webapp/static"), name="static")
templates = Jinja2Templates(directory="subscribers/webapp/templates")

status_func = None
command_func = None

def init(status_fn, command_fn):
    global status_func, command_func
    status_func = status_fn
    command_func = command_fn

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    return {"status": "ready", "message": "Diamond robot is ready"}

@app.get("/api/battery")
async def get_battery():
    return status_func()["battery"]

@app.post("/api/servo")
async def set_servo(data: dict = Body(...)):
    channel = data.get("channel")
    angle = data.get("angle")

    if channel is None or angle is None:
        return {"error": "Missing channel or angle"}

    if channel not in CHANNEL_TO_NAME:
        return {"error": "Invalid channel"}

    servo_name = CHANNEL_TO_NAME[channel]
    command_func({"servo_name": servo_name, "angle": angle})

    return {
        "success": True,
        "channel": channel,
        "angle": angle,
        "name": servo_name
    }

def run():
    uvicorn.run(app, host='0.0.0.0', port=8000)
