# AGENTS.md

## Project
Forza Horizon 6 Blueprint auto-grinder. Captures game frames via OBS WebSocket, detects event-end via OCR ("重新开始"), simulates keyboard input to restart Blueprints automatically.

## Quick Start
```powershell
pip install -r requirements.txt
# Ensure OBS is running with WebSocket enabled and a game capture source named "Forza"
python main.py
```

## Architecture
- `main.py` — entry point, main capture→detect→act loop
- `obs_capture.py` — OBS WebSocket frame grab via `obsws-python`
- `preprocess.py` — crop ROI + grayscale + CLAHE + threshold
- `detector.py` — `rapidocr-onnxruntime` OCR, matches "重新开始" text
- `state_machine.py` — RACING → EVENT_END → RESTARTING → COOLDOWN cycle
- `keyboard_ctrl.py` — `pydirectinput` key presses (X → Enter)
- `config.yaml` — all tunable settings (OBS connection, ROI, keys, timing)
- `utils.py` — config loader, logging setup

## Key Technical Facts
- **Must use `pydirectinput`**, not `pyautogui`. Forza is a DirectX game; `pyautogui` uses SendInput which DirectX ignores. `pydirectinput` uses DirectInput API.
- **`rapidocr-onnxruntime`** — no Tesseract binary needed, good CJK support, fast on CPU.
- **OBS WebSocket must be enabled**: Tools → WebSocket Server Settings → Enable (port 4455).
- **ROI tuning**: Default crop (30-70% x, 40-60% y) targets center-bottom where "奖励" appears. Adjust `ocr.roi` in config if detection is unreliable.
- **Cooldown** (default 8s) prevents re-triggering on stale frames. Increase if menus load slowly.

## Config
All settings in `config.yaml`. Key sections: `obs.*`, `capture.*`, `ocr.*`, `restart.*`, `logging.*`.

## Running
- `python main.py` — start the auto-grinder
- Ctrl+C for graceful shutdown
- Logs to `grinder.log` and stdout
