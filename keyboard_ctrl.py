import logging
import time

import pydirectinput

logger = logging.getLogger("grinder")

pydirectinput.PAUSE = 0.05


def execute_restart_sequence(keys: list[dict]) -> None:
    for step in keys:
        key = step["key"]
        delay = step.get("delay", 0.5)
        logger.info(f"Pressing '{key}' (delay={delay}s)")
        pydirectinput.press(key)
        time.sleep(delay)
