import logging
import time

logger = logging.getLogger("grinder")

STATE_RACING = "RACING"
STATE_RESTARTING = "RESTARTING"
STATE_WAITING_START = "WAITING_START"
STATE_STARTING = "STARTING"
STATE_COOLDOWN = "COOLDOWN"


class StateMachine:
    def __init__(self, cooldown_seconds: float):
        self.state = STATE_RACING
        self.cooldown_seconds = cooldown_seconds
        self._cooldown_start = 0.0

    def update(self, trigger_detected: bool, start_trigger_detected: bool = False) -> str | None:
        if self.state == STATE_RACING:
            if trigger_detected:
                self.state = STATE_RESTARTING
                logger.info("Event end detected, restarting")
                return STATE_RESTARTING

        elif self.state == STATE_RESTARTING:
            self.state = STATE_WAITING_START
            logger.info("Waiting for start trigger")
            return STATE_WAITING_START

        elif self.state == STATE_WAITING_START:
            if start_trigger_detected:
                self.state = STATE_STARTING
                logger.info("Start trigger detected, pressing Enter")
                return STATE_STARTING

        elif self.state == STATE_STARTING:
            self.state = STATE_COOLDOWN
            self._cooldown_start = time.time()
            logger.info(f"Cooldown started ({self.cooldown_seconds}s)")
            return STATE_COOLDOWN

        elif self.state == STATE_COOLDOWN:
            elapsed = time.time() - self._cooldown_start
            if elapsed >= self.cooldown_seconds:
                self.state = STATE_RACING
                logger.info("Cooldown finished, monitoring resumed")
                return STATE_RACING

        return None
