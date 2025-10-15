# database.py

import sqlite3
import bcrypt
import os
from datetime import datetime

# Use absolute path to ensure consistency
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "biomatch.db")

def initialize_db():
    """Initialize all database tables"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # HOSPITALS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            address TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # USERS TABLE (linked to hospital)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'staff',
            hospital_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
        )
    ''')

    # DONATIONS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_name TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            units INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hospital_id INTEGER NOT NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
        )
    ''')

    # INVENTORY TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_type TEXT NOT NULL,
            units_available INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hospital_id INTEGER NOT NULL,
            UNIQUE(blood_type, hospital_id),
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
        )
    ''')

    conn.commit()
    conn.close()


# =============================================
# HOSPITAL MANAGEMENT FUNCTIONS
# =============================================

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
# USER AUTHENTICATION FUNCTIONS
# =============================================

def create_user(username, password, role, hospital_id):
    """Create a new user linked to a hospital"""
    try:
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, hospital_id) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, hospital_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(username, password):
    """Authenticate user and return their details including hospital_id"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return {
                "id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "hospital_id": user['hospital_id']
            }
    return None


# =============================================
# DONATION MANAGEMENT FUNCTIONS
# =============================================

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
        "SELECT * FROM donations WHERE hospital_id = ? ORDER BY date DESC",
        (hospital_id,)
    )
    donations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return donations


# =============================================
# INVENTORY MANAGEMENT FUNCTIONS
# =============================================

def get_inventory_by_hospital(hospital_id):
    """Get blood inventory for a specific hospital"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT blood_type, units_available, last_updated FROM inventory WHERE hospital_id = ? ORDER BY blood_type",
        (hospital_id,)
    )
    inventory = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return inventory


def search_blood_across_hospitals(blood_type, units_needed):
    """Search for compatible blood types across all hospitals"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Define compatibility rules
    compatibility_map = {
        "A+": ["A+", "A-", "O+", "O-"],
        "A-": ["A-", "O-"],
        "B+": ["B+", "B-", "O+", "O-"],
        "B-": ["B-", "O-"],
        "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        "AB-": ["A-", "B-", "AB-", "O-"],
        "O+": ["O+", "O-"],
        "O-": ["O-"]
    }
    
    compatible_types = compatibility_map.get(blood_type, [blood_type])
    
    # Search for compatible blood across hospitals
    placeholders = ','.join('?' * len(compatible_types))
    query = f"""
        SELECT i.blood_type, i.units_available, h.name as hospital_name, h.address, h.contact_number
        FROM inventory i
        JOIN hospitals h ON i.hospital_id = h.id
        WHERE i.blood_type IN ({placeholders}) AND i.units_available >= ?
        ORDER BY i.units_available DESC
    """
    
    cursor.execute(query, (*compatible_types, units_needed))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def search_available_blood_units(blood_type, quantity_needed, priority_level):
    """
    Search for available blood units across all hospitals for a blood request.
    
    This function is used by the /request_blood endpoint to find matching blood inventory
    across all registered hospitals based on the requested blood type.
    
    Args:
        blood_type (str): The requested blood type (e.g., "A+", "O-")
        quantity_needed (int): The number of units required
        priority_level (str): Priority level ("Low", "Medium", "High", "Critical")
    
    Returns:
        list: List of dictionaries containing blood type, hospital name, and units available
              Returns only exact blood type matches (no compatibility mapping)
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query for exact blood type matches across all hospitals
    # Only return hospitals with available units > 0
    query = """
        SELECT 
            i.blood_type,
            h.name as hospital_name,
            i.units_available,
            h.contact_number,
            h.address,
            i.last_updated
        FROM inventory i
        JOIN hospitals h ON i.hospital_id = h.id
        WHERE i.blood_type = ? AND i.units_available > 0
        ORDER BY i.units_available DESC, h.name ASC
    """
    
    cursor.execute(query, (blood_type,))
    results = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries with only required fields for the response
    matched_units = [
        {
            "blood_type": row['blood_type'],
            "hospital_name": row['hospital_name'],
            "units_available": row['units_available']
        }
        for row in results
    ]
    
    return matched_units