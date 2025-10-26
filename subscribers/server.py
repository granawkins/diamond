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

@app.post("/api/leg")
async def set_leg(data: dict = Body(...)):
    leg_name = data.get("leg_name")
    angles = data.get("angles")
    command_func({"leg_name": leg_name, "angles": angles})
    return {"success": True}

def run():
    uvicorn.run(app, host='0.0.0.0', port=8000)
