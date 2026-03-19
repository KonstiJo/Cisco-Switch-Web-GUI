from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from backend.network import get_port_status, set_port_state, get_switch_info, close_all_connections
from backend.database import init_db, log_action, get_logs
from backend.models import SwitchCommand, PortAction

import json

app = FastAPI(title="Switch GUI", version="1.0.0")

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.on_event("startup")
async def startup():
    init_db()


@app.on_event("shutdown")
async def shutdown():
    close_all_connections()


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("frontend/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/dashboard/{switch_ip}", response_class=HTMLResponse)
async def dashboard(switch_ip: str):
    with open("frontend/dashboard.html", encoding="utf-8") as f:
        return f.read()


@app.get("/api/switches")
async def list_switches():
    with open("config/switches.json", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/switches/{switch_ip}/ports")
async def get_ports(switch_ip: str):
    try:
        return get_port_status(switch_ip)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection error: {e}")


@app.post("/api/switches/{switch_ip}/port/{port_id}")
async def set_port(switch_ip: str, port_id: str, action: PortAction):
    try:
        result = set_port_state(switch_ip, port_id, action.state)
        log_action(switch_ip, port_id, action.state)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection error: {e}")


@app.post("/api/switches/{switch_ip}/command")
async def run_command(switch_ip: str, cmd: SwitchCommand):
    try:
        output = get_switch_info(switch_ip, cmd.command)
        log_action(switch_ip, "terminal", cmd.command)
        return {"output": output}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection error: {e}")


@app.get("/api/logs")
async def action_logs(limit: int = 100):
    return get_logs(limit)
