import sqlite3
import os

# Use absolute path to ensure consistency across all imports
DB_NAME = r"backend/biomatch.db"

def initialize_db():
    """Initialize all database tables."""
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
            password TEXT DEFAULT 'hospital123',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add password column to existing hospitals if it doesn't exist
    try:
        cursor.execute("ALTER TABLE hospitals ADD COLUMN password TEXT DEFAULT 'hospital123'")
        print("Added password column to hospitals table")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Update existing hospitals that have NULL password
    cursor.execute("UPDATE hospitals SET password = 'hospital123' WHERE password IS NULL OR password = ''")

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
    
    # Ensure inventory has data for all blood types for each hospital
    cursor.execute('''
        INSERT OR IGNORE INTO inventory (blood_type, units_available, hospital_id)
        SELECT 'A+', 0, h.id FROM hospitals h
        UNION ALL
        SELECT 'A-', 0, h.id FROM hospitals h
        UNION ALL
        SELECT 'B+', 0, h.id FROM hospitals h
        UNION ALL
        SELECT 'B-', 0, h.id FROM hospitals h
        UNION ALL
        SELECT 'AB+', 0, h.id FROM hospitals h
        UNION ALL
        SELECT 'AB-', 0, h.id FROM hospitals h
        UNION ALL
        SELECT 'O+', 0, h.id FROM hospitals h
        UNION ALL
        SELECT 'O-', 0, h.id FROM hospitals h
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

    # DONORS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            hospital_id INTEGER NOT NULL,
            eligibility_status TEXT DEFAULT 'Eligible', -- Eligible/Ineligible/Deferred
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
        )
    ''')

    # BLOOD REQUESTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requesting_hospital_id INTEGER NOT NULL,
            source_hospital_id INTEGER,
            blood_type TEXT NOT NULL,
            units_requested INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            patient_id TEXT NOT NULL,
            requesting_doctor TEXT NOT NULL,
            priority TEXT DEFAULT 'Normal',
            purpose TEXT,
            status TEXT DEFAULT 'pending',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (requesting_hospital_id) REFERENCES hospitals(id),
            FOREIGN KEY (source_hospital_id) REFERENCES hospitals(id)
        )
    """)
    
    # Add notes column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE blood_requests ADD COLUMN notes TEXT DEFAULT ''")
        print("Added notes column to blood_requests table")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Add updated_at column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE blood_requests ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("Added updated_at column to blood_requests table")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized!")
