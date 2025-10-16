import sqlite3
import os
from .db_init import DB_NAME

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