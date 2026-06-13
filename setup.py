"""Setup script to configure OBS WebSocket and Game Capture source for Horizon Grinder."""

import json
import os
import platform
import secrets
import string
import sys
from pathlib import Path

import yaml


def find_obs_config_dir() -> Path | None:
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", ""))
        config_dir = base / "obs-studio"
    elif system == "Darwin":
        config_dir = Path.home() / "Library" / "Application Support" / "obs-studio"
    else:
        config_dir = Path.home() / ".config" / "obs-studio"

    if config_dir.exists():
        return config_dir
    return None


def setup_websocket(config_dir: Path) -> str:
    ws_config_path = config_dir / "plugin_config" / "obs-websocket" / "config.json"

    if ws_config_path.exists():
        with open(ws_config_path, "r", encoding="utf-8") as f:
            ws_config = json.load(f)
    else:
        ws_config = {}

    ws_config["server_enabled"] = True
    ws_config["server_port"] = 4455

    password = ws_config.get("server_password", "")
    if not password:
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for _ in range(16))
        ws_config["server_password"] = password

    ws_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ws_config_path, "w", encoding="utf-8") as f:
        json.dump(ws_config, f, indent=2)

    return ws_config["server_password"]


def setup_scene(config_dir: Path, source_name: str = "Forza"):
    scenes_dir = config_dir / "basic" / "scenes"
    if not scenes_dir.exists():
        print(f"  Warning: Scenes directory not found at {scenes_dir}")
        print("  Please create a scene in OBS first, then re-run this script.")
        return False

    scene_files = list(scenes_dir.glob("*.json"))
    scene_files = [f for f in scene_files if not f.suffix == ".bak"]

    if not scene_files:
        print("  Warning: No scene files found.")
        print("  Please create a scene in OBS first, then re-run this script.")
        return False

    scene_file = scene_files[0]
    print(f"  Using scene file: {scene_file.name}")

    with open(scene_file, "r", encoding="utf-8") as f:
        scene = json.load(f)

    sources = scene.get("sources", [])
    source_names = [s.get("name") for s in sources]

    if source_name in source_names:
        print(f"  Source '{source_name}' already exists, skipping.")
        return True

    uuid = f"{secrets.randbits(32):08x}-{secrets.randbits(16):04x}-{secrets.randbits(16):04x}-{secrets.randbits(16):04x}-{secrets.randbits(48):012x}"

    game_capture = {
        "prev_ver": 536936449,
        "name": source_name,
        "uuid": uuid,
        "id": "game_capture",
        "versioned_id": "game_capture",
        "settings": {},
        "mixers": 0,
        "sync": 0,
        "flags": 0,
        "volume": 1.0,
        "balance": 0.5,
        "enabled": True,
        "muted": False,
        "push-to-mute": False,
        "push-to-mute-delay": 0,
        "push-to-talk": False,
        "push-to-talk-delay": 0,
        "hotkeys": {},
        "deinterlace_mode": 0,
        "deinterlace_field_order": 0,
        "monitoring_type": 0,
        "canvas_uuid": "6c69626f-6273-4c00-9d88-c5136d61696e",
        "private_settings": {},
    }
    sources.append(game_capture)

    for source in sources:
        if source.get("id") == "scene":
            settings = source.get("settings", {})
            items = settings.get("items", [])
            items.append({"name": source_name, "uuid": uuid})
            settings["items"] = items
            settings["id_counter"] = settings.get("id_counter", 0) + 1
            source["settings"] = settings
            break

    scene["sources"] = sources

    with open(scene_file, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)

    return True


def update_project_config(password: str):
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("  Warning: config.yaml not found in current directory.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config.setdefault("obs", {})
    config["obs"]["password"] = password
    config["obs"]["source_name"] = "Forza"

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print("  Updated config.yaml with WebSocket password.")


def main():
    print("=== Horizon Grinder Setup ===\n")

    print("[1/3] Finding OBS config directory...")
    config_dir = find_obs_config_dir()
    if not config_dir:
        print("  ERROR: OBS config directory not found.")
        print("  Please launch OBS at least once to create the config, then re-run.")
        sys.exit(1)
    print(f"  Found: {config_dir}\n")

    print("[2/3] Configuring OBS WebSocket...")
    password = setup_websocket(config_dir)
    print(f"  WebSocket enabled on port 4455")
    print(f"  Password: {password}\n")

    print("[3/3] Adding 'Forza' Game Capture source...")
    ok = setup_scene(config_dir)
    if ok:
        print("  Done.\n")
    else:
        print()

    print("Updating project config.yaml...")
    update_project_config(password)

    print("\n=== Setup Complete ===")
    print("Next steps:")
    print("  1. Launch OBS (or restart if already running)")
    print("  2. Start Forza Horizon 6 in borderless window mode")
    print("  3. In OBS, select the 'Forza' source and choose the game window")
    print("  4. Run: python main.py")


if __name__ == "__main__":
    main()
