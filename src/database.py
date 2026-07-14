import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data") / "marketing_agent.db"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            phone TEXT,
            address TEXT,
            website_url TEXT,
            website_exists INTEGER,
            audit_speed REAL,
            audit_notes TEXT,
            pitch_draft TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def make_hash(name: str, address: str) -> str:
    s = f"{name.strip()}|{address.strip()}"
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def add_lead(name: str, category: str, phone: str, address: str, website_url: str) -> bool:
    """Insert a new lead if it doesn't already exist."""
    lead_id = make_hash(name, address)
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM leads WHERE id = ?", (lead_id,))
        if cursor.fetchone():
            return False  # Already exists
            
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO leads (id, name, category, phone, address, website_url, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'new', ?, ?)
        """, (lead_id, name.strip(), category.strip(), phone.strip(), address.strip(), website_url.strip(), now, now))
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to add lead {name}: {e}")
        return False
    finally:
        conn.close()

def get_leads_by_status(status: str) -> list[dict]:
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM leads WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_leads() -> list[dict]:
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_lead_audit(lead_id: str, website_exists: bool, audit_speed: float, audit_notes: str):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute("""
        UPDATE leads 
        SET website_exists = ?, audit_speed = ?, audit_notes = ?, updated_at = ?
        WHERE id = ?
    """, (1 if website_exists else 0, audit_speed, audit_notes, now, lead_id))
    conn.commit()
    conn.close()

def update_lead_pitch(lead_id: str, pitch_draft: str):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute("""
        UPDATE leads 
        SET pitch_draft = ?, status = 'drafted', updated_at = ?
        WHERE id = ?
    """, (pitch_draft, now, lead_id))
    conn.commit()
    conn.close()

def update_lead_status(lead_id: str, status: str):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute("""
        UPDATE leads 
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (status, now, lead_id))
    conn.commit()
    conn.close()
