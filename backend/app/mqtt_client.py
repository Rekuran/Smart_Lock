import json
import logging
import time
import uuid
import paho.mqtt.client as mqtt
from .database import update_actual_state, log_event

logger = logging.getLogger("BackendMqtt")

class BackendMqttClient:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(client_id="backend-service")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.connected = False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
            self.connected = True
            self.client.subscribe("smartlock/status/+")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
            self.connected = False

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            device_id = payload.get("device_id")
            status = payload.get("status")
            
            if device_id and status:
                logger.info(f"Received status update for {device_id}: {status}")
                update_actual_state(device_id, status)
                log_event("LOCK", "STATUS_RECVD", payload)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def publish_command(self, device_id: str, action: str):
        if not self.connected:
            raise ConnectionError("MQTT client not connected")

        event_id = str(uuid.uuid4())
        payload = {
            "device_id": device_id,
            "action": action,
            "event_id": event_id,
            "timestamp": int(time.time())
        }
        
        topic = f"smartlock/control/{device_id}"
        result = self.client.publish(topic, json.dumps(payload))
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            log_event("BACKEND", "CMD_SENT", payload)
            return event_id
        else:
            raise RuntimeError(f"Failed to publish MQTT message: {result.rc}")

    def start(self):
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Could not connect to MQTT: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
