# Phase 1 Vulnerability Assessment

This document lists the security mechanisms that are **intentionally absent** in the Phase 1 implementation. These vulnerabilities are documented here to serve as a baseline for future research and hardening.

## 1. Transport Layer Security (TLS)
- **Status:** Absent
- **Description:** All communication between the Backend, Broker, and Virtual Lock occurs over plaintext TCP.
- **Vulnerability:** Sensitive data (if any) and control commands can be intercepted using network sniffing tools (e.g., Wireshark).

## 2. Authentication
- **Status:** Absent
- **Description:** No login mechanism for the Management Client, and the MQTT broker allows anonymous connections.
- **Vulnerability:** Any user on the local network can send commands to the backend or directly publish to MQTT topics to control the lock.

## 3. Message Integrity & Authenticity
- **Status:** Absent
- **Description:** Messages do not contain HMACs or digital signatures.
- **Vulnerability:** Commands can be modified in transit (Man-in-the-Middle) or forged entirely.

## 4. Replay Protection
- **Status:** Absent
- **Description:** Although `event_id` and `timestamp` are included in the message schema, they are NOT validated by the receiver.
- **Vulnerability:** An attacker can capture a valid "UNLOCK" command and resend it later to gain unauthorized access.

## 5. Authorization (RBAC)
- **Status:** Absent
- **Description:** There is no check to see if a specific user has permission to control a specific device.
- **Vulnerability:** Privilege escalation or lateral movement is trivial if multiple devices were present.

## 6. Rate Limiting / DoS Protection
- **Status:** Absent
- **Description:** Neither the API nor the Broker has limits on request frequency.
- **Vulnerability:** The system can be easily overwhelmed by a flood of requests.

## 7. Device Identity Verification
- **Status:** Absent
- **Description:** The Backend trusts any device that publishes to the `smartlock/status/` topic.
- **Vulnerability:** A "Rogue Device" can spoof the status of a real lock.
