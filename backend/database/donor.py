import sqlite3
from .db_init import DB_NAME
from datetime import datetime

def add_donor(name, blood_type, hospital_id, eligibility_status='Eligible'):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO donors (name, blood_type, hospital_id, eligibility_status) VALUES (?, ?, ?, ?)",
        (name, blood_type, hospital_id, eligibility_status)
    )
    donor_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return donor_id

def get_all_donors(admin_view=False):
    """
    If admin_view=True, include names. Otherwise, anonymize donor names.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT d.id, d.name, d.blood_type, d.hospital_id, h.name as hospital_name, d.eligibility_status
           FROM donors d
           JOIN hospitals h ON d.hospital_id = h.id'''
    )
    donors = []
    for row in cursor.fetchall():
        donor = {
            "id": row["id"],
            "blood_type": row["blood_type"],
            "hospital_id": row["hospital_id"],
            "hospital_name": row["hospital_name"],
            "eligibility_status": row["eligibility_status"],
        }
        if admin_view:
            donor["name"] = row["name"]
        else:
            donor["name"] = f"Donor #{row['id']}"  # Anonymize
        donors.append(donor)
    conn.close()
    return donors

def update_donor_eligibility(donor_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE donors SET eligibility_status=?, updated_at=? WHERE id=?",
        (new_status, datetime.now().isoformat(), donor_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_donor(donor_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM donors WHERE id=?", (donor_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted