import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("LockHardware")

class LockHardwareSim:
    """
    Simulates the physical lock hardware (actuator).
    In Phase 1, this just manages an internal state and prints to console.
    """
    def __init__(self, device_id: str, initial_state: str = "LOCKED"):
        self.device_id = device_id
        self._state = initial_state
        logger.info(f"[LOCK] Initialized device {self.device_id} in state {self._state}")

    def get_state(self) -> str:
        return self._state

    def set_state(self, new_state: str):
        if new_state not in ["LOCKED", "UNLOCKED"]:
            logger.error(f"[LOCK] Invalid state requested: {new_state}")
            return

        if self._state == new_state:
            logger.info(f"[LOCK] Already in state {new_state}. No action taken.")
            return

        # Simulate hardware delay/actuation
        action_verb = "Locking" if new_state == "LOCKED" else "Unlocking"
        print(f"\n[ACTUATOR] >>> {action_verb} door... <<<")
        
        self._state = new_state
        logger.info(f"[LOCK] Current state: {self._state}")
