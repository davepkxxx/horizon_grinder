import signal
import time

from utils import load_config, setup_logging
from obs_capture import OBSCapture
from preprocess import preprocess
from detector import detect_trigger
from state_machine import (
    StateMachine, STATE_RESTARTING, STATE_STARTING, STATE_RACING
)
from keyboard_ctrl import execute_restart_sequence

_running = True


def _on_signal(sig, frame):
    global _running
    _running = False


def main():
    global _running
    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    config = load_config()
    logger = setup_logging(config)
    logger.info("Horizon Grinder starting")

    obs_cfg = config["obs"]
    cap = OBSCapture(
        host=obs_cfg["host"],
        port=obs_cfg["port"],
        password=obs_cfg["password"],
        source_name=obs_cfg["source_name"],
    )

    ocr_cfg = config["ocr"]
    restart_cfg = config["restart"]
    interval = config["capture"]["interval_seconds"]
    start_trigger = restart_cfg.get("start_trigger", "开始竞赛赛事")

    sm = StateMachine(cooldown_seconds=restart_cfg["cooldown_seconds"])

    logger.info("Entering main loop (Ctrl+C to stop)")
    try:
        while _running:
            frame = cap.grab_frame()
            if frame is None:
                logger.warning("Failed to capture frame, retrying")
                time.sleep(interval)
                continue

            roi = ocr_cfg["roi"]
            processed = preprocess(frame, roi)

            end_detected = detect_trigger(
                processed, ocr_cfg["trigger_texts"], ocr_cfg["confidence_threshold"]
            )
            start_detected = detect_trigger(
                processed, [start_trigger], ocr_cfg["confidence_threshold"]
            )

            action = sm.update(end_detected, start_detected)

            if action == STATE_RESTARTING:
                execute_restart_sequence(restart_cfg["keys"])
                sm.update(False, False)

            elif action == STATE_STARTING:
                execute_restart_sequence([{"key": "enter", "delay": 0.5}])
                sm.update(False, False)

            time.sleep(interval)
    finally:
        cap.close()
        logger.info("Horizon Grinder stopped")


if __name__ == "__main__":
    main()
