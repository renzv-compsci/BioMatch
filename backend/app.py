# app.py

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


from backend.database.db_init import DB_NAME
from database import (
    initialize_db,
    register_hospital,
    get_all_hospitals,
    get_hospital_by_id,
    create_user,
    authenticate_user,
    add_donation,
    get_donations_by_hospital,
    get_inventory_by_hospital,
    search_blood_across_hospitals,
    search_available_blood_units,
    create_transaction,
    get_transactions_by_hospital,
    get_all_transactions,
    update_transaction_status,
    get_transaction_statistics,
    add_donor,
    delete_donor,
    get_all_donors,
    update_donor_eligibility,
)
from routes.blood_requests import blood_request_bp
from routes.hospitals import hospitals_bp
from routes.hospital_auth import hospital_auth_bp

app = Flask(__name__)
CORS(app)
initialize_db()

# Register blueprints
app.register_blueprint(blood_request_bp)
app.register_blueprint(hospitals_bp)
app.register_blueprint(hospital_auth_bp)


# =============================================
# HOSPITAL ENDPOINTS
# =============================================
# These routes handle hospital registration and retrieval
@app.route('/register_hospital', methods=['POST'])  # Register a new hospital
def register_hospital_endpoint():
    """Register a new hospital"""
    data = request.json
    name = data.get('name')
    address = data.get('address')
    contact_person = data.get('contact_person')
    contact_number = data.get('contact_number')
    
    if not all([name, address, contact_person, contact_number]):
        return jsonify({"message": "All fields are required"}), 400
    
    hospital_id = register_hospital(name, address, contact_person, contact_number)
    
    if hospital_id:
        return jsonify({
            "message": "Hospital registered successfully",
            "hospital_id": hospital_id
        }), 201
    else:
        return jsonify({"message": "Hospital name already exists"}), 409


@app.route('/hospitals', methods=['GET'])            # Get list of all hospitals
def get_hospitals():
    """Get list of all hospitals (for dropdown)"""
    hospitals = get_all_hospitals()
    return jsonify(hospitals), 200


@app.route('/hospital/<int:hospital_id>', methods=['GET'])  # Get specific hospital details
def get_hospital(hospital_id):
    """Get hospital details by ID"""
    hospital = get_hospital_by_id(hospital_id)
    if hospital:
        return jsonify(hospital), 200
    else:
        return jsonify({"message": "Hospital not found"}), 404


# =============================================
# USER AUTHENTICATION ENDPOINTS
# =============================================
# These routes handle user login and registration
@app.route('/register', methods=['POST'])   # Register a new user under a hospital
def register():
    """Register a new user under a hospital"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'staff')
    hospital_id = data.get('hospital_id')
    
    if not all([username, password, hospital_id]):
        return jsonify({"message": "Username, password, and hospital_id are required"}), 400
    
    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400
    
    if create_user(username, password, role, hospital_id):
        return jsonify({"message": "User registered successfully"}), 201
    else:
        return jsonify({"message": "Username already exists"}), 409


@app.route('/login', methods=['POST'])      # Authenticate user and return details
def login():
    """Authenticate user and return their details including hospital_id"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    
    user = authenticate_user(username, password)
    
    if user:
        return jsonify({
            "message": "Login successful",
            "user": user
        }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


# =============================================
# DONATION ENDPOINTS
# =============================================
# These routes handle blood donations
@app.route('/donations/<int:hospital_id>', methods=['GET'])
def get_donations(hospital_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, donor_name, blood_type, units, date 
            FROM donations 
            WHERE hospital_id = ? 
            ORDER BY date DESC
        ''', (hospital_id,))
        
        donations = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': d[0],
            'donor_name': d[1],
            'blood_type': d[2],
            'units': d[3],
            'date': d[4]
        } for d in donations])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/donations', methods=['POST'])
@app.route('/add_donation', methods=['POST']) # Handles both modern and legacy routes
def add_donation():
    try:
        data = request.get_json()
        donor_name = data.get('donor_name')
        blood_type = data.get('blood_type')
        units = data.get('units')
        hospital_id = data.get('hospital_id')

        if not all([donor_name, blood_type, units, hospital_id]):
            return jsonify({'error': 'donor_name, blood_type, units and hospital_id are required'}), 400

        try:
            units = int(units)
            hospital_id = int(hospital_id)
            if units <= 0:
                return jsonify({'error': 'units must be > 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'units and hospital_id must be integers'}), 400

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Insert donation
        cursor.execute('''
            INSERT INTO donations (donor_name, blood_type, units, hospital_id)
            VALUES (?, ?, ?, ?)
        ''', (donor_name, blood_type, units, hospital_id))

        # Upsert inventory: check existence then update or insert
        cursor.execute('''
            SELECT id, units_available FROM inventory
            WHERE blood_type = ? AND hospital_id = ?
        ''', (blood_type, hospital_id))
        row = cursor.fetchone()
        if row:
            cursor.execute('''
                UPDATE inventory
                SET units_available = units_available + ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (units, row[0]))
        else:
            cursor.execute('''
                INSERT INTO inventory (blood_type, units_available, hospital_id, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (blood_type, units, hospital_id))

        conn.commit()

        # Return newly created donation id and current inventory summary for convenience
        donation_id = cursor.lastrowid
        cursor.execute('''
            SELECT units_available FROM inventory
            WHERE blood_type = ? AND hospital_id = ?
        ''', (blood_type, hospital_id))
        inv_row = cursor.fetchone()
        units_available = inv_row[0] if inv_row else 0

        conn.close()
        return jsonify({
            'message': 'Donation added successfully',
            'donation_id': donation_id,
            'inventory': {
                'blood_type': blood_type,
                'units_available': units_available,
                'hospital_id': hospital_id
            }
        }), 201

    except Exception as e:
        print(f"Error in add_donation: {e}")
        return jsonify({'error': str(e)}), 500


# Improve create_blood_request: validate, insert, and return the created record (with normalized keys)
@app.route('/blood_requests', methods=['POST'])
def create_blood_request():
    """Create a new blood request and return the created record"""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Accept either 'quantity' or 'units_requested' / 'quantity_needed' for flexibility
        units = data.get('units_requested') or data.get('quantity_needed') or data.get('quantity') 
        priority = data.get('priority') or data.get('priority_level') or 'Normal'
        blood_type = data.get('blood_type')
        requesting_hospital_id = data.get('requesting_hospital_id') or data.get('hospital_id')

        if not all([blood_type, units, requesting_hospital_id]):
            return jsonify({'error': 'blood_type, units_requested (or quantity) and requesting_hospital_id are required'}), 400

        try:
            units = int(units)
            requesting_hospital_id = int(requesting_hospital_id)
            if units <= 0:
                return jsonify({'error': 'units_requested must be > 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'units_requested and requesting_hospital_id must be integers'}), 400

        # Optional fields
        patient_name = data.get('patient_name', 'Unknown')
        patient_id = data.get('patient_id', 'Unknown')
        requesting_doctor = data.get('requesting_doctor', 'Hospital Staff')
        purpose = data.get('purpose', '')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Verify hospital exists
        cursor.execute('SELECT id FROM hospitals WHERE id = ?', (requesting_hospital_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Requesting hospital not found'}), 404

        # Insert the blood request
        cursor.execute('''
            INSERT INTO blood_requests (
                requesting_hospital_id,
                source_hospital_id,
                blood_type,
                units_requested,
                patient_name,
                patient_id,
                requesting_doctor,
                priority,
                purpose,
                status,
                notes
            ) VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        ''', (
            requesting_hospital_id,
            blood_type,
            units,
            patient_name,
            patient_id,
            requesting_doctor,
            priority,
            purpose,
            data.get('notes', '')
        ))

        request_id = cursor.lastrowid
        conn.commit()

        # Fetch the inserted row to return consistent keys expected by frontend
        cursor.execute('''
            SELECT id, requesting_hospital_id, blood_type, units_requested, priority, status, notes, created_at
            FROM blood_requests
            WHERE id = ?
        ''', (request_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            created = {
                'id': row[0],
                'requesting_hospital_id': row[1],
                'blood_type': row[2],
                'units_requested': row[3],
                'quantity_needed': row[3],               # normalize alternative key
                'priority_level': row[4],
                'status': row[5],
                'notes': row[6] or '',
                'created_at': row[7]
            }
            return jsonify({'message': 'Blood request created successfully', 'request': created}), 201
        else:
            return jsonify({'error': 'Failed to fetch created request'}), 500

    except sqlite3.Error as e:
        print(f"Database error in create_blood_request: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        print(f"Server error in create_blood_request: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# Update get_all_blood_requests to include both units_requested and quantity_needed + priority_level normalization
@app.route('/blood_requests', methods=['GET'])
def get_all_blood_requests():
    """Get all blood requests from all hospitals (normalized output)"""
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        limit = request.args.get('limit', 100)

        try:
            limit = int(limit)
        except ValueError:
            limit = 100

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        query = '''
            SELECT 
                br.id,
                br.requesting_hospital_id,
                br.blood_type,
                br.units_requested,
                br.priority,
                br.status,
                br.created_at,
                COALESCE(h.name, 'Unknown Hospital') as requesting_hospital_name,
                COALESCE(br.notes, '') as notes
            FROM blood_requests br
            LEFT JOIN hospitals h ON br.requesting_hospital_id = h.id
            WHERE 1=1
        '''
        params = []

        if status:
            query += ' AND br.status = ?'
            params.append(status)

        if priority:
            query += ' AND br.priority = ?'
            params.append(priority)

        query += ' ORDER BY br.created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        requests_data = cursor.fetchall()

        result = []
        for r in requests_data:
            units_requested = r[3] if r[3] is not None else 0
            result.append({
                'id': r[0],
                'requesting_hospital_id': r[1],
                'blood_type': r[2],
                'units_requested': units_requested,
                'quantity_needed': units_requested,        # provide alternative key
                'priority_level': r[4],
                'status': r[5],
                'created_at': r[6],
                'requesting_hospital_name': r[7],
                'notes': r[8] or ''
            })

        conn.close()
        return jsonify(result), 200

    except sqlite3.OperationalError as e:
        print(f"SQL Error in get_all_blood_requests: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Database schema error: {str(e)}. Please restart the backend.'}), 500
    except Exception as e:
        print(f"Error in get_all_blood_requests: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =============================================
# INVENTORY ENDPOINTS
# =============================================
# These routes handle blood inventory management
@app.route('/inventory/<int:hospital_id>', methods=['GET'])     # Get blood inventory for a hospital
def get_inventory(hospital_id):
    """Get blood inventory for a specific hospital with donation source information"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Get inventory with donation history
        cursor.execute('''
            SELECT 
                i.id,
                i.blood_type,
                i.units_available,
                i.last_updated,
                i.hospital_id,
                h.name as hospital_name
            FROM inventory i
            LEFT JOIN hospitals h ON i.hospital_id = h.id
            WHERE i.hospital_id = ?
            ORDER BY i.blood_type
        ''', (hospital_id,))
        
        inventory = cursor.fetchall()
        
        # Get donation details for each blood type
        result = []
        for item in inventory:
            cursor.execute('''
                SELECT 
                    d.id,
                    d.donor_name,
                    d.blood_type,
                    d.units,
                    d.date,
                    h.name as source_hospital
                FROM donations d
                LEFT JOIN hospitals h ON d.hospital_id = h.id
                WHERE d.blood_type = ? AND d.hospital_id = ?
                ORDER BY d.date DESC
                LIMIT 5
            ''', (item[1], hospital_id))
            
            donations = cursor.fetchall()
            
            result.append({
                'id': item[0],
                'blood_type': item[1],
                'units_available': item[2],
                'last_updated': item[3],
                'hospital_id': item[4],
                'hospital_name': item[5],
                'recent_donations': [{
                    'donor_name': d[1],
                    'units': d[3],
                    'date': d[4],
                    'source_hospital': d[5]
                } for d in donations]
            })
        
        conn.close()
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/search_blood', methods=['POST'])                   # Search for blood across all hospitals
def search_blood():
    """Search for compatible blood across all hospitals"""
    data = request.json
    blood_type = data.get('blood_type')
    units_needed = data.get('units_needed')
    
    if not blood_type or not units_needed:
        return jsonify({"message": "Blood type and units needed are required"}), 400
    
    try:
        units_needed = int(units_needed)
    except ValueError:
        return jsonify({"message": "Units needed must be a number"}), 400
    
    results = search_blood_across_hospitals(blood_type, units_needed)
    return jsonify(results), 200


# =============================================
# BLOOD REQUEST ENDPOINTS
# =============================================
# These routes handle blood requests
@app.route('/request_blood', methods=['POST'])                  # Submit a blood request
def request_blood():
    """
    Process a blood request and return matching available units.
    
    This endpoint enables hospitals or requesters to submit a blood request
    and retrieve a list of matching available blood units across all hospitals.
    
    Request Method: POST
    Justification: POST is chosen because this endpoint processes complex request data,
    may trigger logging/tracking of blood requests in future iterations, and follows
    RESTful conventions for resource queries with multiple parameters.
    
    Expected JSON body:
    {
        "blood_type": "A+",
        "quantity_needed": 3,
        "priority_level": "High",
        "required_date": "2025-10-18"
    }
    
    Returns:
    {
        "message": "Found N hospitals with matching blood units",
        "requested": {
            "blood_type": "A+",
            "quantity_needed": 3,
            "priority_level": "High",
            "required_date": "2025-10-18"
        },
        "results": [
            {
                "blood_type": "A+",
                "hospital_name": "City General Hospital",
                "units_available": 5
            }
        ]
    }
    """
    data = request.json
    
    # Input validation
    blood_type = data.get('blood_type')
    quantity_needed = data.get('quantity_needed')
    priority_level = data.get('priority_level')
    required_date = data.get('required_date')
    
    # Validate required fields
    if not all([blood_type, quantity_needed, priority_level, required_date]):
        return jsonify({
            "message": "All fields are required: blood_type, quantity_needed, priority_level, required_date"
        }), 400
    
    # Validate data types and values
    try:
        quantity_needed = int(quantity_needed)
        if quantity_needed <= 0:
            raise ValueError("Quantity must be positive")
    except (ValueError, TypeError):
        return jsonify({"message": "quantity_needed must be a positive integer"}), 400
    
    # Validate blood type format
    valid_blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    if blood_type not in valid_blood_types:
        return jsonify({
            "message": f"Invalid blood type. Must be one of: {', '.join(valid_blood_types)}"
        }), 400
    
    # Validate priority level
    valid_priorities = ["Low", "Medium", "High", "Critical"]
    if priority_level not in valid_priorities:
        return jsonify({
            "message": f"Invalid priority level. Must be one of: {', '.join(valid_priorities)}"
        }), 400
    
    # Validate date format (basic ISO 8601 format check)
    try:
        from datetime import datetime
        datetime.fromisoformat(required_date.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({
            "message": "Invalid date format. Use ISO 8601 format (e.g., '2025-10-15' or '2025-10-15T10:30:00')"
        }), 400
    
    # Search for matching blood units across all hospitals
    matches = search_available_blood_units(blood_type, quantity_needed, priority_level)
    
    # Create a transaction record for the blood request
    # Note: We'll use hospital_id from request data if provided, otherwise None for now
    requester_hospital_id = data.get('hospital_id')  # Optional field
    
    if requester_hospital_id:
        create_transaction(
            transaction_type='request',
            blood_type=blood_type,
            units=quantity_needed,
            hospital_id=requester_hospital_id,
            status='pending' if not matches else 'completed',
            priority_level=priority_level,
            required_date=required_date,
            notes=f"Blood request for {quantity_needed} units of {blood_type}"
        )
    
    if not matches:
        return jsonify({
            "message": f"No matching blood units found for type {blood_type}",
            "requested": {
                "blood_type": blood_type,
                "quantity_needed": quantity_needed,
                "priority_level": priority_level,
                "required_date": required_date
            },
            "results": []
        }), 200  # Changed to 200 with empty results array instead of 404
    
    # Results are already sorted by units_available DESC, hospital_name ASC in the database function
    
    return jsonify({
        "message": f"Found {len(matches)} hospital(s) with matching blood units",
        "requested": {
            "blood_type": blood_type,
            "quantity_needed": quantity_needed,
            "priority_level": priority_level,
            "required_date": required_date
        },
        "results": matches
    }, 200)


# =============================================
# DASHBOARD ENDPOINTS
# =============================================
# These routes provide dashboard statistics and data
@app.route('/hospital/<int:hospital_id>/dashboard', methods=['GET'])
def get_hospital_dashboard(hospital_id):
    """Get dashboard statistics for a hospital"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Get pending requests
        cursor.execute('''
            SELECT COUNT(*) FROM blood_requests 
            WHERE requesting_hospital_id = ? AND status = "pending"
        ''', (hospital_id,))
        pending_requests = cursor.fetchone()[0]
        
        # Get total requests
        cursor.execute('''
            SELECT COUNT(*) FROM blood_requests 
            WHERE requesting_hospital_id = ?
        ''', (hospital_id,))
        total_requests = cursor.fetchone()[0]
        
        # Get total donations
        cursor.execute('''
            SELECT COUNT(*) FROM donations 
            WHERE hospital_id = ?
        ''', (hospital_id,))
        total_donations = cursor.fetchone()[0]
        
        # Get total blood units
        cursor.execute('''
            SELECT SUM(units_available) FROM inventory 
            WHERE hospital_id = ?
        ''', (hospital_id,))
        blood_units_available = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'statistics': {
                'pending_requests': pending_requests,
                'total_requests': total_requests,
                'total_donations': total_donations,
                'blood_units_available': blood_units_available
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hospital/<int:hospital_id>/requests', methods=['GET'])
def get_hospital_requests(hospital_id):
    """Get all blood requests for a hospital"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Verify hospital exists
        cursor.execute('SELECT id FROM hospitals WHERE id = ?', (hospital_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Hospital not found'}), 404
        
        # Get the requests
        cursor.execute('''
            SELECT 
                id,
                blood_type,
                units_requested,
                priority,
                status,
                created_at,
                patient_name,
                requesting_doctor
            FROM blood_requests 
            WHERE requesting_hospital_id = ?
            ORDER BY created_at DESC
        ''', (hospital_id,))
        
        requests_data = cursor.fetchall()
        
        # Convert to list of dictionaries with keys the frontend expects
        blood_requests = [{
            'id': req[0],
            'blood_type': req[1],
            'quantity_needed': req[2],  # Corrected key for frontend
            'priority_level': req[3],   # Corrected key for frontend
            'status': req[4],
            'created_at': req[5],
            'patient_name': req[6],
            'requesting_doctor': req[7]
        } for req in requests_data]
        
        # Calculate stats
        cursor.execute('''
            SELECT status, COUNT(*) FROM blood_requests 
            WHERE requesting_hospital_id = ?
            GROUP BY status
        ''', (hospital_id,))
        
        status_counts = dict(cursor.fetchall())
        
        stats = {
            'total': len(blood_requests),
            'pending': status_counts.get('pending', 0),
            'approved': status_counts.get('approved', 0),
            'rejected': status_counts.get('rejected', 0)
        }
        
        conn.close()
        
        return jsonify({
            'requests': blood_requests,
            'stats': stats
        }), 200
        
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# Get blood requests TO a hospital (where they can approve/reject)
@app.route('/hospital/<int:hospital_id>/incoming_requests', methods=['GET'])
def get_incoming_requests(hospital_id):
    """Get blood requests that are directed TO this hospital (for approval/rejection)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Get requests where this hospital could be a source (has matching blood type inventory)
        # or requests specifically targeting this hospital
        cursor.execute('''
            SELECT DISTINCT
                br.id,
                br.requesting_hospital_id,
                br.blood_type,
                br.units_requested,
                br.priority,
                br.status,
                br.created_at,
                br.notes,
                rh.name as requesting_hospital_name
            FROM blood_requests br
            LEFT JOIN hospitals rh ON br.requesting_hospital_id = rh.id
            LEFT JOIN inventory i ON i.hospital_id = ? AND i.blood_type = br.blood_type
            WHERE br.requesting_hospital_id != ?
            AND (i.units_available > 0 OR br.source_hospital_id = ?)
            ORDER BY br.created_at DESC
        ''', (hospital_id, hospital_id, hospital_id))
        
        requests_data = cursor.fetchall()
        
        # Calculate stats
        cursor.execute('''
            SELECT br.status, COUNT(*) 
            FROM blood_requests br
            LEFT JOIN inventory i ON i.hospital_id = ? AND i.blood_type = br.blood_type
            WHERE br.requesting_hospital_id != ?
            AND (i.units_available > 0 OR br.source_hospital_id = ?)
            GROUP BY br.status
        ''', (hospital_id, hospital_id, hospital_id))
        
        status_counts = dict(cursor.fetchall())
        
        # Format response
        requests_list = []
        for req in requests_data:
            requests_list.append({
                'id': req[0],
                'requesting_hospital_id': req[1],
                'blood_type': req[2],
                'units_requested': req[3],
                'quantity_needed': req[3],
                'priority': req[4],
                'priority_level': req[4],
                'status': req[5],
                'created_at': req[6],
                'notes': req[7] or '',
                'requesting_hospital_name': req[8] or f'Hospital {req[1]}'
            })
        
        stats = {
            'total': len(requests_list),
            'pending': status_counts.get('pending', 0),
            'approved': status_counts.get('approved', 0),
            'rejected': status_counts.get('rejected', 0)
        }
        
        conn.close()
        
        return jsonify({
            'requests': requests_list,
            'stats': stats
        }), 200
        
    except Exception as e:
        print(f"Error getting incoming requests: {e}")
        return jsonify({'error': str(e)}), 500


# Get completed blood request transactions for a hospital (both sent and received)
@app.route('/hospital/<int:hospital_id>/transactions', methods=['GET'])
def get_blood_request_transactions(hospital_id):
    """Get completed blood request transactions (approved/rejected/completed only)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Get filter parameters
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        
        # Build query to get both sent and received requests (excluding pending)
        query = '''
            SELECT DISTINCT
                br.id,
                br.requesting_hospital_id,
                br.source_hospital_id,
                br.blood_type,
                br.units_requested,
                br.priority,
                br.status,
                br.created_at,
                br.notes,
                rh.name as requesting_hospital_name,
                sh.name as source_hospital_name
            FROM blood_requests br
            LEFT JOIN hospitals rh ON br.requesting_hospital_id = rh.id
            LEFT JOIN hospitals sh ON br.source_hospital_id = sh.id
            WHERE (br.requesting_hospital_id = ? OR br.source_hospital_id = ?)
            AND br.status != 'pending'
        '''
        
        params = [hospital_id, hospital_id]
        
        # Add filters
        if status_filter and status_filter != 'All':
            query += ' AND br.status = ?'
            params.append(status_filter)
        
        if priority_filter and priority_filter != 'All':
            query += ' AND br.priority = ?'
            params.append(priority_filter)
        
        query += ' ORDER BY br.created_at DESC'
        
        cursor.execute(query, params)
        transactions_data = cursor.fetchall()
        
        # Calculate stats
        cursor.execute('''
            SELECT br.status, COUNT(*) 
            FROM blood_requests br
            WHERE (br.requesting_hospital_id = ? OR br.source_hospital_id = ?)
            AND br.status != 'pending'
            GROUP BY br.status
        ''', (hospital_id, hospital_id))
        
        status_counts = dict(cursor.fetchall())
        
        # Format response
        transactions_list = []
        for txn in transactions_data:
            transactions_list.append({
                'id': txn[0],
                'requesting_hospital_id': txn[1],
                'source_hospital_id': txn[2],
                'blood_type': txn[3],
                'units_requested': txn[4],
                'priority': txn[5],
                'priority_level': txn[5],
                'status': txn[6],
                'created_at': txn[7],
                'notes': txn[8] or '',
                'requesting_hospital_name': txn[9] or f'Hospital {txn[1]}',
                'source_hospital_name': txn[10] or f'Hospital {txn[2]}'
            })
        
        stats = {
            'total': len(transactions_list),
            'approved': status_counts.get('approved', 0),
            'rejected': status_counts.get('rejected', 0),
            'completed': status_counts.get('completed', 0)
        }
        
        conn.close()
        
        return jsonify({
            'transactions': transactions_list,
            'stats': stats
        }), 200
        
    except Exception as e:
        print(f"Error getting transactions: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================
# TRANSACTION HISTORY ENDPOINTS
# =============================================
# These routes handle transaction tracking
@app.route('/transactions/<int:hospital_id>', methods=['GET'])  # Get transactions for a hospital
def get_hospital_transactions(hospital_id):
    """
    Get transaction history for a specific hospital with optional filters.
    
    Query Parameters:
        - type: Filter by transaction type ('donation', 'request', 'transfer')
        - status: Filter by status ('pending', 'completed', 'cancelled')
        - limit: Maximum number of records (default: 100)
    
    Example: /transactions/1?type=donation&status=completed&limit=50
    """
    transaction_type = request.args.get('type')
    status = request.args.get('status')
    limit = request.args.get('limit', 100)
    
    try:
        limit = int(limit)
        if limit <= 0 or limit > 500:
            limit = 100
    except ValueError:
        limit = 100
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Build the query with hospital name join
        query = '''
            SELECT 
                t.id,
                t.transaction_type,
                t.blood_type,
                t.units,
                t.status,
                t.priority_level,
                t.created_at,
                h.name as hospital_name,
                t.notes
            FROM transactions t
            LEFT JOIN hospitals h ON t.hospital_id = h.id
            WHERE t.hospital_id = ?
        '''
        
        params = [hospital_id]
        
        # Add filters
        if transaction_type:
            query += ' AND t.transaction_type = ?'
            params.append(transaction_type)
        
        if status:
            query += ' AND t.status = ?'
            params.append(status)
        
        query += ' ORDER BY t.created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        result = [{
            'id': t[0],
            'transaction_type': t[1],
            'blood_type': t[2],
            'units': t[3],
            'status': t[4],
            'priority_level': t[5],
            'created_at': t[6],
            'hospital_name': t[7],
            'notes': t[8]
        } for t in transactions]
        
        conn.close()
        
        return jsonify({
            "hospital_id": hospital_id,
            "count": len(result),
            "transactions": result
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/transactions', methods=['GET'])
def get_all_transactions_endpoint():
    """
    Get all transactions across all hospitals (admin view).
    
    Query Parameters:
        - type: Filter by transaction type ('donation', 'request', 'transfer')
        - status: Filter by status ('pending', 'completed', 'cancelled')
        - limit: Maximum number of records (default: 100)
    """
    transaction_type = request.args.get('type')
    status = request.args.get('status')
    limit = request.args.get('limit', 100)
    
    try:
        limit = int(limit)
        if limit <= 0 or limit > 500:
            limit = 100
    except ValueError:
        limit = 100
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Build the query with hospital name join
        query = '''
            SELECT 
                t.id,
                t.transaction_type,
                t.blood_type,
                t.units,
                t.status,
                t.priority_level,
                t.created_at,
                h.name as hospital_name,
                t.notes
            FROM transactions t
            LEFT JOIN hospitals h ON t.hospital_id = h.id
            WHERE 1=1
        '''
        
        params = []
        
        # Add filters
        if transaction_type:
            query += ' AND t.transaction_type = ?'
            params.append(transaction_type)
        
        if status:
            query += ' AND t.status = ?'
            params.append(status)
        
        query += ' ORDER BY t.created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        result = [{
            'id': t[0],
            'transaction_type': t[1],
            'blood_type': t[2],
            'units': t[3],
            'status': t[4],
            'priority_level': t[5],
            'created_at': t[6],
            'hospital_name': t[7],
            'notes': t[8]
        } for t in transactions]
        
        conn.close()
        
        return jsonify({
            "count": len(result),
            "transactions": result
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/transactions/<int:transaction_id>/status', methods=['PUT'])
def update_transaction_status_endpoint(transaction_id):
    """
    Update the status of a transaction.
    
    Expected JSON body:
    {
        "status": "completed",
        "notes": "Optional notes about the status change"
    }
    """
    data = request.json
    new_status = data.get('status')
    notes = data.get('notes')
    
    if not new_status:
        return jsonify({"message": "Status is required"}), 400
    
    if new_status not in ['pending', 'completed', 'cancelled']:
        return jsonify({
            "message": "Invalid status. Must be 'pending', 'completed', or 'cancelled'"
        }), 400
    
    success = update_transaction_status(transaction_id, new_status, notes)
    
    if success:
        return jsonify({
            "message": "Transaction status updated successfully",
            "transaction_id": transaction_id,
            "new_status": new_status
        }), 200
    else:
        return jsonify({"message": "Transaction not found or update failed"}), 404


@app.route('/transactions/statistics', methods=['GET'])
@app.route('/transactions/statistics/<int:hospital_id>', methods=['GET'])
def get_statistics(hospital_id=None):
    """
    Get transaction statistics.
    
    If hospital_id is provided: Returns stats for that hospital
    If hospital_id is not provided: Returns system-wide stats
    """
    stats = get_transaction_statistics(hospital_id)
    
    return jsonify({
        "hospital_id": hospital_id,
        "statistics": stats
    }), 200


# =============================================
# DONOR ENDPOINTS
# =============================================
# These routes handle donor management
@app.route('/donors', methods=['GET'])                          # List all donors
def list_donors():
    # Suppose admin status is checked via session or a query param for demo
    admin = request.args.get('admin') == "1"
    donors = get_all_donors(admin_view=admin)
    return jsonify(donors), 200


@app.route('/donor', methods=['POST'])                          # Create a new donor
def create_donor():
    data = request.json
    donor_id = add_donor(
        name=data['name'],
        blood_type=data['blood_type'],
        hospital_id=data['hospital_id'],
        eligibility_status=data.get('eligibility_status', 'Eligible')
    )
    return jsonify({"donor_id": donor_id}), 201


@app.route('/donor/<int:donor_id>/eligibility', methods=['PUT']) # Update donor eligibility
def set_donor_eligibility(donor_id):
    data = request.json
    updated = update_donor_eligibility(donor_id, data['eligibility_status'])
    return jsonify({"updated": updated}), 200


@app.route('/donor/<int:donor_id>', methods=['DELETE'])         # Delete a donor
def remove_donor(donor_id):
    deleted = delete_donor(donor_id)
    return jsonify({"deleted": deleted}), 200


# =============================================
# TEST ENDPOINT
# =============================================
@app.route('/ping', methods=['GET'])                            # Health check
def ping():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "pong"}), 200


# Update blood request status (approve/reject/pending/cancelled)
@app.route('/blood_requests/<int:request_id>/status', methods=['PUT'])
def update_blood_request_status(request_id: int):
    try:
        data = request.get_json(silent=True) or {}
        new_status = str(data.get('status', '')).lower()
        allowed = {'pending', 'approved', 'rejected', 'cancelled'}
        if new_status not in allowed:
            return jsonify({'error': f"Invalid status. Allowed: {', '.join(sorted(allowed))}"}), 400

        # Get the hospital ID of who is approving this request
        approving_hospital_id = data.get('approving_hospital_id')
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetch the request to get blood_type and requesting_hospital_id
        cursor.execute('''
            SELECT id, blood_type, units_requested, requesting_hospital_id, status 
            FROM blood_requests WHERE id = ?
        ''', (request_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Blood request not found'}), 404

        request_id_db, blood_type, units_requested, requesting_hospital_id, old_status = row

        # If approving, transfer blood from approving hospital to requesting hospital
        if new_status == 'approved' and old_status != 'approved':
            if not approving_hospital_id:
                conn.close()
                return jsonify({'error': 'Approving hospital ID is required for approval'}), 400
                
            # Check and decrease inventory from the APPROVING hospital
            cursor.execute('''
                SELECT id, units_available FROM inventory
                WHERE blood_type = ? AND hospital_id = ?
            ''', (blood_type, approving_hospital_id))
            approving_inv_row = cursor.fetchone()
            
            if approving_inv_row:
                approving_inv_id, units_available = approving_inv_row
                if units_available >= units_requested:
                    # Decrease inventory from the APPROVING hospital
                    cursor.execute('''
                        UPDATE inventory
                        SET units_available = units_available - ?, last_updated = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (units_requested, approving_inv_id))
                    
                    # Increase inventory for the REQUESTING hospital
                    cursor.execute('''
                        SELECT id, units_available FROM inventory
                        WHERE blood_type = ? AND hospital_id = ?
                    ''', (blood_type, requesting_hospital_id))
                    requesting_inv_row = cursor.fetchone()
                    
                    if requesting_inv_row:
                        # Update existing inventory
                        requesting_inv_id = requesting_inv_row[0]
                        cursor.execute('''
                            UPDATE inventory
                            SET units_available = units_available + ?, last_updated = CURRENT_TIMESTAMP
                            WHERE id = ?
                        ''', (units_requested, requesting_inv_id))
                    else:
                        # Create new inventory record for requesting hospital
                        cursor.execute('''
                            INSERT INTO inventory (blood_type, units_available, hospital_id, last_updated)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (blood_type, units_requested, requesting_hospital_id))
                        
                else:
                    conn.close()
                    return jsonify({'error': f'Insufficient inventory. Available: {units_available}, Requested: {units_requested}'}), 400
            else:
                conn.close()
                return jsonify({'error': 'Approving hospital inventory not found'}), 404
        
        # If rejecting after approval, reverse the blood transfer
        elif new_status == 'rejected' and old_status == 'approved':
            if approving_hospital_id:
                # Return blood to the APPROVING hospital
                cursor.execute('''
                    SELECT id FROM inventory
                    WHERE blood_type = ? AND hospital_id = ?
                ''', (blood_type, approving_hospital_id))
                approving_inv_row = cursor.fetchone()
                
                if approving_inv_row:
                    approving_inv_id = approving_inv_row[0]
                    cursor.execute('''
                        UPDATE inventory
                        SET units_available = units_available + ?, last_updated = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (units_requested, approving_inv_id))
                
                # Remove blood from the REQUESTING hospital
                cursor.execute('''
                    SELECT id, units_available FROM inventory
                    WHERE blood_type = ? AND hospital_id = ?
                ''', (blood_type, requesting_hospital_id))
                requesting_inv_row = cursor.fetchone()
                
                if requesting_inv_row:
                    requesting_inv_id, current_units = requesting_inv_row
                    if current_units >= units_requested:
                        cursor.execute('''
                            UPDATE inventory
                            SET units_available = units_available - ?, last_updated = CURRENT_TIMESTAMP
                            WHERE id = ?
                        ''', (units_requested, requesting_inv_id))

        # Update status
        cursor.execute('''
            UPDATE blood_requests
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_status, request_id))
        conn.commit()

        # Return updated record with normalized keys
        cursor.execute('''
            SELECT id, requesting_hospital_id, blood_type, units_requested, priority, status, notes, created_at
            FROM blood_requests WHERE id = ?
        ''', (request_id,))
        r = cursor.fetchone()
        conn.close()

        updated = {
            'id': r[0],
            'requesting_hospital_id': r[1],
            'blood_type': r[2],
            'units_requested': r[3],
            'quantity_needed': r[3],
            'priority_level': r[4],
            'status': r[5],
            'notes': r[6] or '',
            'created_at': r[7]
        }
        return jsonify({'message': 'Status updated', 'request': updated}), 200
    except Exception as e:
        print(f"Error updating blood request status: {e}")
        return jsonify({'error': str(e)}), 500


# Update blood request notes
@app.route('/blood_requests/<int:request_id>/notes', methods=['PUT'])
def update_blood_request_notes(request_id: int):
    try:
        data = request.get_json(silent=True) or {}
        notes = data.get('notes', '')
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM blood_requests WHERE id = ?', (request_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Blood request not found'}), 404

        cursor.execute('''
            UPDATE blood_requests
            SET notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (notes, request_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Notes updated'}), 200
    except Exception as e:
        print(f"Error updating blood request notes: {e}")
        return jsonify({'error': str(e)}), 500


# Notify hospital (stub for frontend compatibility)
@app.route('/blood_requests/<int:request_id>/notify', methods=['POST'])
def notify_blood_request(request_id: int):
    try:
        # You can integrate real notification logic here
        return jsonify({'message': 'Notification queued'}), 200
    except Exception as e:
        print(f"Error notifying hospital: {e}")
        return jsonify({'error': str(e)}), 500

# Make sure this block is executed when running directly
if __name__ == '__main__':
    print("Starting BioMatch backend on http://127.0.0.1:5000/")
    app.run(debug=True)
    print("Flask server has shut down")