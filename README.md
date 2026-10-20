# Cisco Switch Web GUI

Lokales Web-GUI zur Verwaltung mehrerer Cisco-Switches (z. B. 3750X-/2960X-Stacks) über SSH –
ohne CLI, mit Port-Übersicht und Browser-Terminal.

## Tech-Stack

| Schicht | Technologie | Zweck |
|---|---|---|
| Backend | **FastAPI** (Python) | Async-API + WebSocket-Support |
| SSH / CLI | **Netmiko** (+ Paramiko) | Verbindungsaufbau, Cisco-IOS-Kommandos, Config-Mode |
| CLI-Parsing | **ntc-templates** | Parst `show`-Ausgaben in strukturierte Daten |
| Frontend | **Bootstrap 5 + Vanilla JS** | Kein Build-Tool nötig |
| Terminal | **xterm.js** (CDN) + WebSocket | Browser-Terminal, per SSH-Stream-Relay an die Switches |
| Datenbank | **SQLite** | Logging / Änderungsprotokoll |
| Server | **Uvicorn** | ASGI-Server |

## Struktur

```
Cisco-Switch-Web-GUI/
├── backend/
│   ├── main.py        ← FastAPI-App, Routen
│   ├── network.py     ← Netmiko-Verbindungen, Parsing
│   ├── models.py       ← Datenmodelle
│   └── database.py    ← SQLite-Logging
├── frontend/
│   ├── index.html     ← Switch-Auswahl
│   ├── dashboard.html ← Port-Grid + Terminal
│   └── static/        ← JS/CSS
├── config/
│   └── switches.json  ← Switch-Inventar (Hostname, IP, Modell, Stack-Flag)
├── requirements.txt
└── start.bat           ← Startet Uvicorn unter Windows
```

## Funktionsumfang

- Switch-Inventar aus `config/switches.json`
- Port-Status, VLAN, Speed und Description je Port (`show interfaces status`, geparst via
  ntc-templates, kurzzeitig gecacht)
- Port-Grid-Visualisierung im Browser (grün = connected, rot = notconnect, grau = disabled)
- Port-Konfiguration direkt aus der GUI: Description setzen, VLAN ändern, shutdown/no shutdown
- Browser-Terminal per WebSocket (`/ws/terminal/{switch_id}`) als SSH-Stream-Relay
- Änderungslog in SQLite (wer/was/wann)

## Voraussetzungen

- Python 3 (siehe `requirements.txt`: `fastapi`, `uvicorn[standard]`, `netmiko`, `paramiko`,
  `python-dotenv`, `ntc-templates`)
- SSH-Zugriff auf die Switches; Credentials werden über eine lokale `.env`-Datei geladen
  (nicht Teil des Repos)

## Starten

```bash
pip install -r requirements.txt
```

Unter Windows per Doppelklick auf `start.bat`, alternativ direkt:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Danach `http://localhost:8000` im Browser öffnen.

## Hinweise

- Kein kontinuierliches Polling – Daten werden beim Laden der Seite bzw. über einen manuellen
  „Refresh"-Button abgerufen, um dauerhafte SSH-Verbindungen zu vermeiden.
- Reine Single-User-/Trusted-Network-Lösung ohne eigenes Auth-System – nicht für den Einsatz in
  nicht vertrauenswürdigen Netzen gedacht.
