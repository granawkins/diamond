from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn

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

@app.get("/api/ping")
async def ping():
    return {"message": "pong"}

@app.get("/api/status")
async def get_status():
    return status_func()

@app.post("/api/command")
async def execute_command(data: dict = Body(...)):
    command = data.get("command")
    command_func(command)
    return {"success": True}

def run():
    uvicorn.run(app, host='0.0.0.0', port=8000)

if __name__ == "__main__":
    run()