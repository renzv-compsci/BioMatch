import sqlite3
import bcrypt
import os
from .db_init import DB_NAME

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