import json
import time
import paho.mqtt.client as mqtt

def test_simple_unlock():
    """
    A simple manual-style test script to verify the lock reacts to MQTT.
    """
    client = mqtt.Client()
    client.connect("localhost", 1883)
    
    test_command = {
        "device_id": "lock-001",
        "action": "UNLOCK",
        "event_id": "test-uuid-123",
        "timestamp": int(time.time())
    }
    
    print(f"Sending test UNLOCK command to smartlock/control/lock-001...")
    client.publish("smartlock/control/lock-001", json.dumps(test_command))
    client.disconnect()
    print("Command sent.")

if __name__ == "__main__":
    test_simple_unlock()
