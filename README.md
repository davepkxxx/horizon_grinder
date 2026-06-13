# Horizon Grinder

Forza Horizon 6 Blueprint auto-grinder. Automatically restarts and replays Blueprints by detecting game UI via OCR and simulating keyboard input.

## How it works

1. Captures game frames via OBS WebSocket
2. Detects event-end screen ("重新开始") using OCR
3. Simulates key presses to navigate menus and restart the Blueprint
4. Waits for race-start screen ("开始竞赛赛事") and confirms
5. Repeats after cooldown

## Requirements

- Windows 10/11
- Forza Horizon 6 (borderless window mode)
- OBS Studio with WebSocket enabled
- Python 3.10+

## Setup

### 1. Install OBS Studio
Enable WebSocket: **Tools → WebSocket Server Settings → Enable** (port 4455)

Add a **Game Capture** source named `Forza` (or match `source_name` in config).

### 2. Install dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure
Edit `config.yaml`:
- `obs.password` — your OBS WebSocket password
- `obs.source_name` — OBS source name (default: "Forza")
- `ocr.roi` — region of interest for text detection (tune if detection is unreliable)
- `restart.keys` — key sequence and delays
- `restart.cooldown_seconds` — pause between cycles

### 4. Run
```powershell
python main.py
```

Ctrl+C to stop. Logs are written to `grinder.log` and stdout.

## Config reference

| Setting | Default | Description |
|---------|---------|-------------|
| `obs.host` | localhost | OBS WebSocket host |
| `obs.port` | 4455 | OBS WebSocket port |
| `obs.password` | — | OBS WebSocket password |
| `obs.source_name` | Forza | OBS capture source name |
| `capture.interval_seconds` | 0.3 | Seconds between frame captures |
| `ocr.roi.*` | — | Crop region (fraction of frame) |
| `ocr.trigger_texts` | 重新开始 | Text to detect event-end |
| `ocr.confidence_threshold` | 0.7 | OCR confidence minimum |
| `restart.keys` | X→Enter | Key sequence to restart |
| `restart.cooldown_seconds` | 10 | Cooldown between cycles |
| `restart.start_trigger` | 开始竞赛赛事 | Text to detect race-start |

## Troubleshooting

- **Black screenshots**: Ensure Forza is running and OBS Game Capture is active
- **OCR not detecting text**: Adjust `ocr.roi` to cover where the text appears on screen
- **Keys not working**: `pydirectinput` requires the game to be in focus. Don't Alt+Tab.
- **Slow detection**: Keep screenshot resolution at 1080p, not 4K

## License

MIT
