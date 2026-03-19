import os
import json
import threading
import time

from netmiko import ConnectHandler
from dotenv import load_dotenv

load_dotenv()

# ── Verbindungspool ───────────────────────────────────────────────────────────
# Jede SSH-Session wird bis zu _CONN_TTL Sekunden wiederverwendet,
# damit nicht bei jedem API-Request neu verbunden wird.

_CONN_TTL = 300  # 5 Minuten Leerlauf bevor neu verbunden wird

_connections: dict = {}  # switch_ip -> ConnectHandler
_last_used: dict = {}    # switch_ip -> monotonic time
_locks: dict = {}        # switch_ip -> threading.Lock
_global_lock = threading.Lock()


def _ensure_lock(switch_ip: str) -> threading.Lock:
    """Per-Switch-Lock um Race Conditions zu verhindern."""
    with _global_lock:
        if switch_ip not in _locks:
            _locks[switch_ip] = threading.Lock()
        return _locks[switch_ip]


def _get_device(switch_ip: str) -> dict:
    """Switch aus Inventar laden und Netmiko-Device-Dict bauen."""
    with open("config/switches.json", encoding="utf-8") as f:
        switches = json.load(f)

    switch = next((s for s in switches if s["ip"] == switch_ip), None)
    if not switch:
        raise ValueError(f"Switch {switch_ip} nicht im Inventar gefunden")

    return {
        "device_type": switch.get("device_type", "cisco_ios"),
        "host": switch_ip,
        "username": os.getenv("SWITCH_USER"),
        "password": os.getenv("SWITCH_PASSWORD"),
        "secret": os.getenv("SWITCH_SECRET", ""),
    }


def _get_connection(switch_ip: str) -> ConnectHandler:
    """Gecachte Verbindung zurückgeben oder neu aufbauen."""
    lock = _ensure_lock(switch_ip)
    with lock:
        now = time.monotonic()
        conn = _connections.get(switch_ip)

        if conn is not None:
            age = now - _last_used.get(switch_ip, 0)
            if age < _CONN_TTL:
                try:
                    conn.find_prompt()  # Verbindung testen
                    _last_used[switch_ip] = now
                    return conn
                except Exception:
                    try:
                        conn.disconnect()
                    except Exception:
                        pass
            _connections.pop(switch_ip, None)
            _last_used.pop(switch_ip, None)

        # Neue SSH-Verbindung aufbauen
        device = _get_device(switch_ip)
        conn = ConnectHandler(**device)
        if device.get("secret"):
            conn.enable()
        _connections[switch_ip] = conn
        _last_used[switch_ip] = now
        return conn


def close_all_connections():
    """Alle gepoolten SSH-Verbindungen geordnet schließen (Shutdown-Hook)."""
    with _global_lock:
        for conn in _connections.values():
            try:
                conn.disconnect()
            except Exception:
                pass
        _connections.clear()
        _last_used.clear()


# ── Öffentliche API-Hilfsfunktionen ───────────────────────────────────────────

def get_port_status(switch_ip: str) -> list:
    """Gibt geparste Interface-Status-Liste via TextFSM zurück."""
    conn = _get_connection(switch_ip)
    output = conn.send_command("show interfaces status", use_textfsm=True)
    return output if isinstance(output, list) else []


def set_port_state(switch_ip: str, port_id: str, state: str) -> dict:
    """Interface herunterfahren oder hochbringen."""
    if state not in ("up", "down"):
        raise ValueError("state muss 'up' oder 'down' sein")
    cmd = "no shutdown" if state == "up" else "shutdown"
    conn = _get_connection(switch_ip)
    conn.enable()
    conn.send_config_set([f"interface {port_id}", cmd])
    return {"port": port_id, "state": state, "switch": switch_ip}


def get_switch_info(switch_ip: str, command: str) -> str:
    """Beliebigen Show-Befehl ausführen und Rohausgabe zurückgeben."""
    conn = _get_connection(switch_ip)
    return conn.send_command(command)

