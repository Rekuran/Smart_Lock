import json
import logging
import time
import paho.mqtt.client as mqtt
from lock_hardware import LockHardwareSim

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("MqttManager")

class LockMqttClient:
    """
    Handles MQTT communication for the Virtual Lock.
    Phase 1: Insecure, no TLS, no Auth.
    """
    def __init__(self, broker_host: str, broker_port: int, hardware: LockHardwareSim):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.hardware = hardware
        self.device_id = hardware.device_id
        
        self.control_topic = f"smartlock/control/{self.device_id}"
        self.status_topic = f"smartlock/status/{self.device_id}"
        
        self.client = mqtt.Client(client_id=f"lock-sim-{self.device_id}")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"[MQTT] Connected to broker at {self.broker_host}:{self.broker_port}")
            self.client.subscribe(self.control_topic)
            logger.info(f"[MQTT] Subscribed to {self.control_topic}")
            # Publish initial state
            self.publish_status("INIT-EVENT-000")
        else:
            logger.error(f"[MQTT] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        logger.warning(f"[MQTT] Disconnected from broker (code {rc})")

    def _on_message(self, client, userdata, msg):
        logger.info(f"[MQTT] Received message on {msg.topic}")
        logger.info(f"[MQTT] Raw payload: {msg.payload!r}")
        try:
            payload = json.loads(msg.payload.decode())
            self._handle_command(payload)
        except json.JSONDecodeError:
            logger.error("[MQTT] Failed to decode JSON payload")
        except Exception as e:
            logger.error(f"[MQTT] Error processing message: {e}")

    def _handle_command(self, payload: dict):
        """
        Phase 1: Minimal validation, no security checks.
        """
        # 1. Basic Structure Validation
        required_keys = ["device_id", "action", "event_id", "timestamp"]
        if not all(k in payload for k in required_keys):
            logger.error("[MQTT] Malformed command: Missing required keys")
            return

        if payload["device_id"] != self.device_id:
            logger.warning(f"[MQTT] Ignored command for different device: {payload['device_id']}")
            return

        # 2. Extract Data (Phase 1 ignores timestamp/event_id for logic)
        action = payload["action"]
        event_id = payload["event_id"]

        # 3. Trigger Hardware
        if action == "LOCK":
            self.hardware.set_state("LOCKED")
        elif action == "UNLOCK":
            self.hardware.set_state("UNLOCKED")
        else:
            logger.error(f"[MQTT] Unknown action: {action}")
            return

        # 4. Report Status Back
        self.publish_status(event_id)

    def publish_status(self, event_id: str):
        status_payload = {
            "device_id": self.device_id,
            "status": self.hardware.get_state(),
            "event_id": event_id,
            "timestamp": int(time.time())
        }
        self.client.publish(self.status_topic, json.dumps(status_payload))
        logger.info(f"[MQTT] Published status '{status_payload['status']}' to {self.status_topic}")

    def run(self):
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_forever()
        except Exception as e:
            logger.error(f"[MQTT] Runtime error: {e}")

if __name__ == "__main__":
    # In a real scenario, these would come from env vars or a config file
    BROKER = "localhost"
    PORT = 1883
    DEVICE_ID = "lock-001"

    lock_hw = LockHardwareSim(device_id=DEVICE_ID)
    mqtt_mgr = LockMqttClient(BROKER, PORT, lock_hw)
    
    mqtt_mgr.run()
