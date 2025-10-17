from datetime import datetime
import sqlite3
import os
from .db_init import DB_NAME

def add_donation(donor_name, blood_type, units, hospital_id):
    """Add a donation and automatically update inventory"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Insert donation record
        cursor.execute(
            "INSERT INTO donations (donor_name, blood_type, units, hospital_id) VALUES (?, ?, ?, ?)",
            (donor_name, blood_type, units, hospital_id)
        )
        
        # Update inventory
        cursor.execute(
            "UPDATE inventory SET units_available = units_available + ?, last_updated = ? WHERE blood_type = ? AND hospital_id = ?",
            (units, datetime.now().isoformat(), blood_type, hospital_id)
        )
        
        # Create transaction record for donation
        cursor.execute(
            "INSERT INTO transactions (transaction_type, blood_type, units, hospital_id, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
            ('donation', blood_type, units, hospital_id, 'completed', f'Donation from {donor_name}')
        )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding donation: {e}")
        return False
    finally:
        conn.close()

def get_donations_by_hospital(hospital_id):
    """Get all donations for a specific hospital"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM donations WHERE hospital_id = ? ORDER BY donation_date DESC",
        (hospital_id,)
    )
    donations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return donations