import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "../biomatch.db")

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

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized!")
