import sqlite3
import json
import time
from datetime import datetime

DATABASE_NAME = "smartlock.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Locks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locks (
            device_id TEXT PRIMARY KEY,
            desired_state TEXT,
            actual_state TEXT,
            last_synced TIMESTAMP
        )
    ''')
    
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP,
            source TEXT,
            event_type TEXT,
            payload TEXT
        )
    ''')
    
    # Initial device
    cursor.execute("SELECT device_id FROM locks WHERE device_id = 'lock-001'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO locks (device_id, desired_state, actual_state, last_synced)
            VALUES (?, ?, ?, ?)
        ''', ('lock-001', 'LOCKED', 'LOCKED', datetime.now()))
    
    conn.commit()
    conn.close()

class DatabaseManager:
    def __enter__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

def get_locks():
    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM locks")
        return [dict(row) for row in cursor.fetchall()]

def get_lock(device_id: str):
    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM locks WHERE device_id = ?", (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_desired_state(device_id: str, state: str):
    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE locks SET desired_state = ? WHERE device_id = ?
        ''', (state, device_id))

def update_actual_state(device_id: str, state: str):
    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE locks SET actual_state = ?, last_synced = ? WHERE device_id = ?
        ''', (state, datetime.now(), device_id))

def log_event(source: str, event_type: str, payload: dict):
    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (timestamp, source, event_type, payload)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), source, event_type, json.dumps(payload)))

def get_events():
    with DatabaseManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]
