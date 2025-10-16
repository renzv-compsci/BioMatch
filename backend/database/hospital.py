import sqlite3
import os
from .db_init import DB_NAME

def register_hospital(name, address, contact_person, contact_number):
    """Register a new hospital in the system"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO hospitals (name, address, contact_person, contact_number) VALUES (?, ?, ?, ?)",
            (name, address, contact_person, contact_number)
        )
        hospital_id = cursor.lastrowid
        conn.commit()
        
        # Initialize inventory for all blood types
        blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        for blood_type in blood_types:
            cursor.execute(
                "INSERT INTO inventory (blood_type, units_available, hospital_id) VALUES (?, 0, ?)",
                (blood_type, hospital_id)
            )
        conn.commit()
        
        return hospital_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_all_hospitals():
    """Get list of all registered hospitals"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address FROM hospitals")
    hospitals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return hospitals

def get_hospital_by_id(hospital_id):
    """Get hospital details by ID"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospitals WHERE id = ?", (hospital_id,))
    hospital = cursor.fetchone()
    conn.close()
    return dict(hospital) if hospital else None