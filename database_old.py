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

    # TRANSACTIONS TABLE - Track all blood-related operations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            units INTEGER NOT NULL,
            hospital_id INTEGER NOT NULL,
            target_hospital_id INTEGER,
            status TEXT DEFAULT 'completed',
            priority_level TEXT,
            required_date TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
            FOREIGN KEY (target_hospital_id) REFERENCES hospitals(id)
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

# =============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "biomatch.db")


def create_transaction(transaction_type, blood_type, units, hospital_id, 
                       target_hospital_id=None, status='completed', 
                       priority_level=None, required_date=None, notes=None):
    """
    Create a new transaction record.
    
    Args:
        transaction_type (str): Type of transaction - 'donation', 'request', 'transfer'
        blood_type (str): Blood type (e.g., 'A+', 'O-')
        units (int): Number of units
        hospital_id (int): ID of the hospital initiating the transaction
        target_hospital_id (int, optional): ID of target hospital (for transfers)
        status (str): Transaction status - 'pending', 'completed', 'cancelled'
        priority_level (str, optional): Priority level for requests
        required_date (str, optional): Required date for requests
        notes (str, optional): Additional notes
    
    Returns:
        int: Transaction ID if successful, None otherwise
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions 
            (transaction_type, blood_type, units, hospital_id, target_hospital_id, 
             status, priority_level, required_date, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_type, blood_type, units, hospital_id, target_hospital_id,
              status, priority_level, required_date, notes, datetime.now().isoformat()))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        return transaction_id
    except Exception as e:
        print(f"Error creating transaction: {e}")
        return None
    finally:
        conn.close()


def get_transactions_by_hospital(hospital_id, transaction_type=None, status=None, limit=100):
    """
    Get transaction history for a specific hospital with optional filters.
    
    Args:
        hospital_id (int): ID of the hospital
        transaction_type (str, optional): Filter by type - 'donation', 'request', 'transfer'
        status (str, optional): Filter by status - 'pending', 'completed', 'cancelled'
        limit (int): Maximum number of records to return (default: 100)
    
    Returns:
        list: List of transaction dictionaries
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query with optional filters
    query = """
        SELECT 
            t.id,
            t.transaction_type,
            t.blood_type,
            t.units,
            t.status,
            t.priority_level,
            t.required_date,
            t.notes,
            t.created_at,
            t.updated_at,
            h1.name as hospital_name,
            h2.name as target_hospital_name
        FROM transactions t
        JOIN hospitals h1 ON t.hospital_id = h1.id
        LEFT JOIN hospitals h2 ON t.target_hospital_id = h2.id
        WHERE t.hospital_id = ?
    """
    
    params = [hospital_id]
    
    if transaction_type:
        query += " AND t.transaction_type = ?"
        params.append(transaction_type)
    
    if status:
        query += " AND t.status = ?"
        params.append(status)
    
    query += " ORDER BY t.created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return transactions


def get_all_transactions(transaction_type=None, status=None, limit=100):
    """
    Get all transactions across all hospitals with optional filters.
    Useful for system-wide monitoring and admin views.
    
    Args:
        transaction_type (str, optional): Filter by type
        status (str, optional): Filter by status
        limit (int): Maximum number of records
    
    Returns:
        list: List of transaction dictionaries
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT 
            t.id,
            t.transaction_type,
            t.blood_type,
            t.units,
            t.status,
            t.priority_level,
            t.required_date,
            t.notes,
            t.created_at,
            t.updated_at,
            h1.name as hospital_name,
            h2.name as target_hospital_name
        FROM transactions t
        JOIN hospitals h1 ON t.hospital_id = h1.id
        LEFT JOIN hospitals h2 ON t.target_hospital_id = h2.id
        WHERE 1=1
    """
    
    params = []
    
    if transaction_type:
        query += " AND t.transaction_type = ?"
        params.append(transaction_type)
    
    if status:
        query += " AND t.status = ?"
        params.append(status)
    
    query += " ORDER BY t.created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return transactions


def update_transaction_status(transaction_id, new_status, notes=None):
    """
    Update the status of a transaction.
    
    Args:
        transaction_id (int): ID of the transaction
        new_status (str): New status - 'pending', 'completed', 'cancelled'
        notes (str, optional): Additional notes about the status change
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        update_query = """
            UPDATE transactions 
            SET status = ?, updated_at = ?
        """
        params = [new_status, datetime.now().isoformat()]
        
        if notes:
            update_query += ", notes = ?"
            params.append(notes)
        
        update_query += " WHERE id = ?"
        params.append(transaction_id)
        
        cursor.execute(update_query, params)
        conn.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating transaction status: {e}")
        return False
    finally:
        conn.close()

12
def get_transaction_statistics(hospital_id=None):
    """
    Get transaction statistics for analytics.
    
    Args:
        hospital_id (int, optional): If provided, stats for specific hospital; 
                                     otherwise system-wide stats
    
    Returns:
        dict: Dictionary containing various statistics
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if hospital_id:
        # Hospital-specific statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN transaction_type = 'donation' THEN 1 ELSE 0 END) as total_donations,
                SUM(CASE WHEN transaction_type = 'request' THEN 1 ELSE 0 END) as total_requests,
                SUM(CASE WHEN transaction_type = 'transfer' THEN 1 ELSE 0 END) as total_transfers,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_transactions,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_transactions,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_transactions,
                SUM(CASE WHEN transaction_type = 'donation' THEN units ELSE 0 END) as total_donated_units,
                SUM(CASE WHEN transaction_type = 'request' THEN units ELSE 0 END) as total_requested_units
            FROM transactions
            WHERE hospital_id = ?
        """, (hospital_id,))
    else:
        # System-wide statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN transaction_type = 'donation' THEN 1 ELSE 0 END) as total_donations,
                SUM(CASE WHEN transaction_type = 'request' THEN 1 ELSE 0 END) as total_requests,
                SUM(CASE WHEN transaction_type = 'transfer' THEN 1 ELSE 0 END) as total_transfers,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_transactions,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_transactions,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_transactions,
                SUM(CASE WHEN transaction_type = 'donation' THEN units ELSE 0 END) as total_donated_units,
                SUM(CASE WHEN transaction_type = 'request' THEN units ELSE 0 END) as total_requested_units
            FROM transactions
        """)
    
    stats = cursor.fetchone()
    conn.close()
    
    return dict(stats) if stats else {}

if __name__ == "__main__":
    initialize_db()
    hospital_id = register_hospital("Test Hospital", "123 Test St", "Dr. Test", "09123456789")
    print("Hospital ID:", hospital_id)
    print("All hospitals:", get_all_hospitals())