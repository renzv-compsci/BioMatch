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


# =============================================
# BLOOD REQUEST FUNCTIONS
# =============================================

def create_blood_request(requesting_hospital_id, source_hospital_id, blood_type, units_requested, 
                        patient_name, patient_id, requesting_doctor, priority, purpose):
    """Create a new blood request"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO blood_requests 
               (requesting_hospital_id, source_hospital_id, blood_type, units_requested, 
                patient_name, patient_id, requesting_doctor, priority, purpose, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (requesting_hospital_id, source_hospital_id, blood_type, units_requested,
             patient_name, patient_id, requesting_doctor, priority, purpose)
        )
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return request_id
    except Exception as e:
        print(f"Error creating blood request: {e}")
        return None


def get_blood_requests_by_hospital(hospital_id):
    """Get all blood requests for a hospital (both requesting and source)"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT br.*, 
               h1.name as requesting_hospital_name,
               h2.name as source_hospital_name
        FROM blood_requests br
        LEFT JOIN hospitals h1 ON br.requesting_hospital_id = h1.id
        LEFT JOIN hospitals h2 ON br.source_hospital_id = h2.id
        WHERE br.requesting_hospital_id = ? OR br.source_hospital_id = ?
        ORDER BY br.created_at DESC
    """, (hospital_id, hospital_id))
    
    requests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return requests


def get_blood_request_by_id(request_id):
    """Get blood request details by ID"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT br.*,
               h1.name as requesting_hospital_name, h1.contact_number as requesting_contact,
               h2.name as source_hospital_name, h2.contact_number as source_contact
        FROM blood_requests br
        LEFT JOIN hospitals h1 ON br.requesting_hospital_id = h1.id
        LEFT JOIN hospitals h2 ON br.source_hospital_id = h2.id
        WHERE br.id = ?
    """, (request_id,))
    
    request = cursor.fetchone()
    conn.close()
    return dict(request) if request else None


def update_blood_request_status(request_id, status):
    """Update blood request status"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE blood_requests SET status = ? WHERE id = ?",
            (status, request_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating blood request: {e}")
        return False


def get_pending_requests_count(hospital_id):
    """Get count of pending blood requests for a hospital"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM blood_requests WHERE (requesting_hospital_id = ? OR source_hospital_id = ?) AND status = 'pending'",
        (hospital_id, hospital_id)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_request_statistics(hospital_id):
    """Get blood request statistics for a hospital"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_requests,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
        FROM blood_requests 
        WHERE requesting_hospital_id = ? OR source_hospital_id = ?
    """, (hospital_id, hospital_id))
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        'total_requests': stats[0] or 0,
        'pending': stats[1] or 0,
        'approved': stats[2] or 0,
        'completed': stats[3] or 0,
        'rejected': stats[4] or 0
    }


def search_blood_availability(blood_type, units_needed):
    """Search for blood availability across all hospitals"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            i.hospital_id,
            h.name as hospital_name,
            h.address,
            h.contact_number,
            i.blood_type,
            i.units_available
        FROM inventory i
        JOIN hospitals h ON i.hospital_id = h.id
        WHERE i.blood_type = ? AND i.units_available >= ?
        ORDER BY i.units_available DESC
    """, (blood_type, units_needed))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def ensure_hospital_passwords():
    """Ensure all hospitals have the default password"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Try to add password column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE hospitals ADD COLUMN password TEXT DEFAULT 'hospital123'")
        except sqlite3.OperationalError:
            pass
        
        # Update all hospitals to have the default password
        cursor.execute("UPDATE hospitals SET password = 'hospital123' WHERE password IS NULL OR password = ''")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error ensuring hospital passwords: {e}")


def authenticate_hospital(hospital_id, password):
    """Authenticate a hospital"""
    # Ensure passwords are set before authentication
    ensure_hospital_passwords()
    
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM hospitals WHERE id = ? AND password = ?",
            (hospital_id, password)
        )
        hospital = cursor.fetchone()
        conn.close()
        return dict(hospital) if hospital else None
    except Exception as e:
        print(f"Error authenticating hospital: {e}")
        return None


def update_hospital_password(hospital_id, old_password, new_password):
    """Update hospital password"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Verify old password
        cursor.execute(
            "SELECT * FROM hospitals WHERE id = ? AND password = ?",
            (hospital_id, old_password)
        )
        
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Update password
        cursor.execute(
            "UPDATE hospitals SET password = ? WHERE id = ?",
            (new_password, hospital_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating hospital password: {e}")
        return False