# AGENTS.md

## Project
Forza Horizon 6 Blueprint auto-grinder. Captures game frames via OBS WebSocket, detects event-end via OCR ("重新开始"), simulates keyboard input to restart Blueprints automatically.

## Quick Start
```powershell
pip install -r requirements.txt
python setup.py          # Auto-configures OBS WebSocket + Game Capture source
python main.py
```

## Architecture
- `main.py` — entry point, main capture→detect→act loop
- `obs_capture.py` — OBS WebSocket frame grab via `obsws-python`
- `preprocess.py` — crop ROI + grayscale + CLAHE + threshold
- `detector.py` — `rapidocr-onnxruntime` OCR, matches "重新开始" and "开始竞赛赛事"
- `state_machine.py` — RACING → RESTARTING → WAITING_START → STARTING → COOLDOWN cycle
- `keyboard_ctrl.py` — `pydirectinput` key presses (X → Enter → Enter)
- `config.yaml` — all tunable settings (OBS connection, ROI, keys, timing)
- `utils.py` — config loader, logging setup

## Key Technical Facts
- **Must use `pydirectinput`**, not `pyautogui`. Forza is a DirectX game; `pyautogui` uses SendInput which DirectX ignores. `pydirectinput` uses DirectInput API.
- **`rapidocr-onnxruntime`** — no Tesseract binary needed, good CJK support, fast on CPU.
- **OBS WebSocket must be enabled**: Tools → WebSocket Server Settings → Enable (port 4455).
- **Screenshot resolution**: Must use 1920x1080. 3840x2160 works but is ~10x slower (~9.5s per grab vs ~0.2s).
- **ROI tuning**: Default crop (x=0.03, y=0.55, w=0.50, h=0.40) covers left side where both "重新开始" (y≈0.92) and "开始竞赛赛事" (y≈0.61) appear.
- **Two-phase restart**: First detects "重新开始" → presses X then Enter. Then waits for "开始竞赛赛事" → presses Enter to start race.
- **Cooldown** (default 10s) prevents re-triggering on stale frames.
- **Capture interval** (0.3s) balances responsiveness vs CPU usage.

## Config
All settings in `config.yaml`. Key sections: `obs.*`, `capture.*`, `ocr.*`, `restart.*`, `logging.*`.

## Running
- `python main.py` — start the auto-grinder
- Ctrl+C for graceful shutdown
- Logs to `grinder.log` and stdout
