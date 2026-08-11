from fastapi import FastAPI, HTTPException, status
from typing import List
from .database import init_db, get_locks, get_lock, update_desired_state, get_events
from .mqtt_client import BackendMqttClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartLockAPI")

app = FastAPI(title="Smart Lock Phase 1 API")

# Global MQTT client
mqtt_client = BackendMqttClient()

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Starting MQTT client...")
    mqtt_client.start()

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Stopping MQTT client...")
    mqtt_client.stop()

@app.get("/locks")
def list_locks():
    return get_locks()

@app.get("/locks/{device_id}")
def read_lock(device_id: str):
    lock = get_lock(device_id)
    if not lock:
        raise HTTPException(status_code=404, detail="Lock not found")
    return lock

@app.post("/locks/{device_id}/toggle", status_code=status.HTTP_202_ACCEPTED)
def toggle_lock(device_id: str):
    lock = get_lock(device_id)
    if not lock:
        raise HTTPException(status_code=404, detail="Lock not found")
    
    current_desired = lock.get("desired_state")
    new_state = "UNLOCKED" if current_desired == "LOCKED" else "LOCKED"
    
    # Update desired state in DB
    update_desired_state(device_id, new_state)
    
    # Publish to MQTT
    mqtt_action = "LOCK" if new_state == "LOCKED" else "UNLOCK"
    try:
        mqtt_client.publish_command(device_id, mqtt_action)
    except ConnectionError:
        raise HTTPException(
            status_code=503, 
            detail="MQTT broker unavailable"
        )
    except Exception as e:
        logger.error(f"Failed to publish command: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during command publication"
        )
    
    return {"device_id": device_id, "new_desired_state": new_state}

@app.get("/events")
def list_events():
    return get_events()
