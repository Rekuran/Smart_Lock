# Smart Lock IoT Security Project - Phase 1

This project is a research-oriented Smart Lock IoT system designed to be developed incrementally. Phase 1 focuses on establishing a "Functional but Intentionally Insecure" baseline for security research and attack simulation.

## Overview

Phase 1 provides a complete end-to-end communication loop between a management interface and a virtual lock hardware simulator. This system is designed to be the foundation for future security hardening exercises.

## Architecture

The system consists of the following components:

**Management Interface (Swagger UI) -> FastAPI Backend -> Mosquitto MQTT Broker -> Virtual Smart Lock**

### Components

- **Virtual Smart Lock (`virtual_lock/`):** A Python-based simulator that represents the physical lock hardware. It listens for MQTT commands and reports its status back to the broker.
- **FastAPI Backend (`backend/`):** The central controller of the system. It exposes a REST API, manages the lock state in a database, and communicates with the lock via MQTT.
- **Mosquitto MQTT Broker:** A lightweight messaging broker (running in Docker) that handles the communication between the backend and the virtual lock.
- **SQLite Database (`smartlock.db`):** Stores the current `desired_state` and `actual_state` of the locks, along with a log of all system events.

## Implemented Features

- **Virtual Hardware:** Python simulator for `lock-001`.
- **MQTT Communication:** Asynchronous messaging between the backend and the lock.
- **State Tracking:** Persistence of both "desired" (what the user wants) and "actual" (what the lock reports) states.
- **Event Logging:** All commands and status updates are logged in the SQLite database.
- **REST API Endpoints:**
    - `GET /locks`: List all registered locks.
    - `GET /locks/{device_id}`: Get the current state of a specific lock.
    - `POST /locks/{device_id}/toggle`: Command a lock to change state (LOCKED/UNLOCKED).
    - `GET /events`: View the system event log.
- **MQTT Topics:**
    - `smartlock/control/{device_id}`: Used by the backend to send commands (LOCK/UNLOCK).
    - `smartlock/status/{device_id}`: Used by the lock to report its current status.

## Verified End-to-End Flow

The following communication loop has been successfully tested:
1. User sends a **Toggle Request** via the FastAPI Swagger UI.
2. **FastAPI** updates the `desired_state` in the **SQLite** database.
3. **FastAPI** publishes a command to the **Mosquitto** broker.
4. **Virtual Lock** receives the command and updates its internal state.
5. **Virtual Lock** publishes a status update back to **Mosquitto**.
6. **FastAPI** receives the status update and updates the `actual_state` in **SQLite**.

## Running the Project

Follow these steps to run the Phase 1 system:

### 1. Start the MQTT Broker
Ensure Docker is installed and running, then start the Mosquitto broker:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 2. Start the Virtual Lock
In a new terminal window:
```bash
python virtual_lock\lock_sim.py
```

### 3. Start the FastAPI Backend
In another new terminal window:
```bash
python -m uvicorn backend.app.main:app --reload
```

### 4. Open the Management Interface
Navigate to the FastAPI Swagger UI in your browser:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

From here, you can use the `POST /locks/lock-001/toggle` endpoint to control the virtual lock.

## Phase 1 Security Status

**WARNING: Phase 1 is intentionally insecure.**

The current implementation lacks all modern security protections to serve as a baseline for security testing and hardening. The following vulnerabilities are present by design:
- **No Authentication:** Anyone can access the API and the MQTT broker.
- **No Authorization:** There are no permissions or roles.
- **No TLS/Encryption:** All communication is sent in plain text (vulnerable to sniffing).
- **No Message Integrity:** MQTT messages can be intercepted and modified.
- **No Replay Protection:** Commands can be captured and re-sent to control the lock.
- **No Rate Limiting:** The system is vulnerable to brute-force and DoS attacks.

## Project Roadmap

### Phase 1: Infrastructure (Completed)
- [x] Virtual Lock Simulator
- [x] MQTT Communication Layer
- [x] SQLite Database Integration
- [x] FastAPI Backend Development
- [x] End-to-End Functional Verification

### Phase 2: Attack Simulation (Future)
- [ ] Management CLI Development
- [ ] Sniffing and Traffic Analysis
- [ ] Replay Attack Demonstration
- [ ] Unauthorized Access Simulation

### Phase 3: Security Hardening (Future)
- [ ] Authentication & Authorization (JWT)
- [ ] TLS/mTLS for MQTT and REST
- [ ] Message Integrity Protection
- [ ] Replay Protection Mechanisms
- [ ] ML-based Anomaly Detection

### Phase 4: Hardware Integration (Future)
- [ ] ESP32/Physical Hardware Integration
