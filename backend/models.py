from pydantic import BaseModel
from typing import Optional


class SwitchCommand(BaseModel):
    command: str


class PortAction(BaseModel):
    state: str  # "up" or "down"


class SwitchEntry(BaseModel):
    ip: str
    name: str
    device_type: str = "cisco_ios"
    location: Optional[str] = None


class LogEntry(BaseModel):
    timestamp: str
    switch_ip: str
    target: str
    action: str
