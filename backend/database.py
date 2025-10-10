"""
pip instasll bcrypt pls 

Module sets up SQLite database this includes secure password hashing
, and convinient CRUD operations 
"""
import os
import sqlite3
import bcrypt
from typing import Optional, List, Tuple, Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_BIOMATCH = os.path.join(DB_DIR, "biomatch.db")

os.makedirs(DB_DIR, exist_ok=True)

# Database initialization 
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    address TEXT,
    location_x REAL,
    location_y REAL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL, -- 'admin', 'hospital_staff', etc.
    hospital_id INTEGER,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
);

CREATE TABLE IF NOT EXISTS donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id_hash TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    blood_type TEXT NOT NULL,
    hospital_id INTEGER,
    last_donation_date TEXT,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER,
    blood_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    last_updated TEXT,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
    UNIQUE(hospital_id, blood_type)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_id_hash TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    hospital_id INTEGER NOT NULL,
    donor_id_hash TEXT,
    related_hospital_id INTEGER,
    blood_type TEXT NOT NULL,
    units INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
    FOREIGN KEY (donor_id_hash) REFERENCES donors(donor_id_hash),
    FOREIGN KEY (related_hospital_id) REFERENCES hospitals(id)
);
"""

# creates db connection
def db_connection():
    conn = sqlite3.connect(DB_BIOMATCH)
    conn.row_factory = sqlite3.Row
    return conn 

def initialize_db():
    try:
        with db_connection() as conn:
            conn.executescript(SCHEMA_SQL)
        print("Database initialized")
    except Exception as e:
        print(f"Database initializatiion failed {e}")

# security utilities 
def hash_pass(password: str) -> bytes:
    # Hashes password using bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_pass(password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)

# user management 
def create_user(username: str, password: str, role: str, hospital_id: Optional[int] = None) -> bool:
    # creates user with hashed password 
    password_hash = hash_pass(password)
    try: 
        with db_connection() as conn:
            conn.execute (
                "INSERT INTO users (username,password_hash, role, hospital_id) VALUES (?, ?, ?, ?)",
                (username, password_hash, role, hospital_id)
            )
            return True
    except sqlite3.IntegrityError:
        # if username already exists
        return False

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    # authenticates user by username and password 
    with db_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cur.fetchone()
        if user and verify_pass(password, user["password_hash"]):
            return dict(user)
    return None

# hospital management 
def add_hospital(name: str, address: str, location_x: float, location_y: float) -> bool:
    # add hospital 
    try:
        with db_connection() as conn:
            conn.execute(
                "INSERT INTO hospitals (name, address, location_x, location_y) VALUES (?, ?, ?, ?)",
                (name, address, location_x, location_y)
            )
        return True
    except sqlite3.IntegrityError:
        return False

def get_hospital(name: str) -> Optional[Dict]:
    with db_connection() as conn:
        cur = conn.execute("SELECT* FROM hospitals WHERE name = ?", (name,))
        row = cur.fetchone()
        return dict(row) if row else None

def get_all_hospital() -> List[Dict]:
    with db_connection() as conn:
        cur = conn.execute ("SELECT * FROM hospitals")
        return [dict(row) for row in cur.fetchall()]

if __name__ == "__main__":
    initialize_db

    # Acc for admin
    admin_username = "admin"
    admin_password = "adminpass"
    admin_role = "admin"

    # check if admin exists, else create
    with db_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
        if not cur.fetchone():
            print("Creating default admin user...")
            created = create_user(admin_username, admin_password, admin_role)
            print("Admin created." if created else "Failed to create admin (username exists).")

    # Add a hospital
    if add_hospital("St. Luke's Hospital", "Quezon Ave, QC", 14.6517, 121.0497):
        print("Hospital added.")
    else:
        print("Hospital already exists.")

    # authenticate the admin
    user = authenticate_user(admin_username, admin_password)
    if user:
        print(f"Authenticated as: {user['username']} (Role: {user['role']})")
    else:
        print("Authentication failed.")