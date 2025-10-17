import sqlite3
import os

def fix_hospital_passwords():
    """Add password column and set default password for all hospitals"""
    try:
        # Try multiple possible database paths
        possible_paths = [
            "database/biomatch.db",
            "backend/database/biomatch.db",
            os.path.join(os.path.dirname(__file__), 'biomatch.db'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'biomatch.db')
        ]
        
        db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            print("✗ Database file not found!")
            print(f"Searched in: {possible_paths}")
            print(f"\nCurrent directory: {os.getcwd()}")
            return
        
        print(f"✓ Using database: {db_path}\n")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Try to add password column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE hospitals ADD COLUMN password TEXT DEFAULT 'hospital123'")
            print("✓ Added password column to hospitals table")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("✓ Password column already exists")
            else:
                print(f"Error adding column: {e}")
        
        # Update all hospitals to have the default password
        cursor.execute("UPDATE hospitals SET password = 'hospital123' WHERE password IS NULL OR password = ''")
        affected = cursor.rowcount
        print(f"✓ Updated {affected} hospital(s) with default password")
        
        # Verify hospitals
        cursor.execute("SELECT id, name, password FROM hospitals")
        hospitals = cursor.fetchall()
        print(f"\n✓ Total hospitals in database: {len(hospitals)}")
        for hospital in hospitals:
            print(f"  - Hospital ID {hospital[0]}: {hospital[1]} | Password: {hospital[2]}")
        
        conn.commit()
        conn.close()
        
        print("\n✓ Hospital passwords fixed successfully!")
        print("\nYou can now login with:")
        print("  Hospital ID: (your hospital ID)")
        print("  Password: hospital123")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_hospital_passwords()
