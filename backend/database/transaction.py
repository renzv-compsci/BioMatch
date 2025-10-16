from datetime import datetime
import sqlite3
import os
from .db_init import DB_NAME

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