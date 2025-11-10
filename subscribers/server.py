from fastapi import FastAPI, Body
from fastapi.responses import FileResponse
import uvicorn
from pathlib import Path

app = FastAPI()

state_func = None
command_func = None

def init(state_fn, command_fn):
    global state_func, command_func
    state_func = state_fn
    command_func = command_fn

@app.get("/api/state")
async def get_state():
    return state_func()

@app.post("/api/command")
async def execute_command(data: dict = Body(...)):
    command = data.get("command")
    print(f"Executing command: {command}")
    command_func(command)
    return {"success": True}

# Serve static files from ../web/dist for non-API routes
@app.get("/{full_path:path}")
async def serve_static(full_path: str):
    # Get the path to web/dist directory (relative to this file)
    base_dir = Path(__file__).parent.parent / "web" / "dist"
    
    # If path is empty or is a directory, serve index.html
    if not full_path or full_path == "":
        file_path = base_dir / "index.html"
    else:
        file_path = base_dir / full_path
    
    return FileResponse(file_path)

def run():
    uvicorn.run(app, host='0.0.0.0', port=8000)
