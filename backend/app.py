# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
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

app = Flask(__name__)
CORS(app)
initialize_db()


# =============================================
# HOSPITAL ENDPOINTS
# =============================================

@app.route('/register_hospital', methods=['POST'])
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


@app.route('/hospitals', methods=['GET'])
def get_hospitals():
    """Get list of all hospitals (for dropdown)"""
    hospitals = get_all_hospitals()
    return jsonify(hospitals), 200


@app.route('/hospital/<int:hospital_id>', methods=['GET'])
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

@app.route('/register', methods=['POST'])
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


@app.route('/login', methods=['POST'])
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

@app.route('/add_donation', methods=['POST'])
def add_donation_endpoint():
    """Add a donation and update inventory"""
    data = request.json
    donor_name = data.get('donor_name')
    blood_type = data.get('blood_type')
    units = data.get('units')
    hospital_id = data.get('hospital_id')
    
    if not all([donor_name, blood_type, units, hospital_id]):
        return jsonify({"message": "All fields are required"}), 400
    
    try:
        units = int(units)
        hospital_id = int(hospital_id)
    except ValueError:
        return jsonify({"message": "Units and hospital_id must be numbers"}), 400
    
    if add_donation(donor_name, blood_type, units, hospital_id):
        return jsonify({"message": "Donation added successfully"}), 201
    else:
        return jsonify({"message": "Failed to add donation"}), 500


@app.route('/donations/<int:hospital_id>', methods=['GET'])
def get_donations(hospital_id):
    """Get all donations for a hospital"""
    donations = get_donations_by_hospital(hospital_id)
    return jsonify(donations), 200


# =============================================
# INVENTORY ENDPOINTS
# =============================================

@app.route('/inventory/<int:hospital_id>', methods=['GET'])
def get_inventory(hospital_id):
    """Get blood inventory for a specific hospital"""
    inventory = get_inventory_by_hospital(hospital_id)
    return jsonify(inventory), 200


@app.route('/search_blood', methods=['POST'])
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

@app.route('/request_blood', methods=['POST'])
@app.route('/api/v1/blood/request', methods=['POST'])
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
    }), 200


# =============================================
# TRANSACTION HISTORY ENDPOINTS
# =============================================

@app.route('/transactions/<int:hospital_id>', methods=['GET'])
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
    
    # Validate transaction_type if provided
    if transaction_type and transaction_type not in ['donation', 'request', 'transfer']:
        return jsonify({
            "message": "Invalid transaction type. Must be 'donation', 'request', or 'transfer'"
        }), 400
    
    # Validate status if provided
    if status and status not in ['pending', 'completed', 'cancelled']:
        return jsonify({
            "message": "Invalid status. Must be 'pending', 'completed', or 'cancelled'"
        }), 400
    
    transactions = get_transactions_by_hospital(hospital_id, transaction_type, status, limit)
    
    return jsonify({
        "hospital_id": hospital_id,
        "count": len(transactions),
        "transactions": transactions
    }), 200


@app.route('/transactions', methods=['GET'])
def get_all_transactions_endpoint():
    """
    Get all transactions across all hospitals (admin view).
    
    Query Parameters:
        - type: Filter by transaction type
        - status: Filter by status
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
    
    transactions = get_all_transactions(transaction_type, status, limit)
    
    return jsonify({
        "count": len(transactions),
        "transactions": transactions
    }), 200


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
# TEST ENDPOINT
# =============================================

@app.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "pong"}), 200

@app.route('/donors', methods=['GET'])
def list_donors():
    # Suppose admin status is checked via session or a query param for demo
    admin = request.args.get('admin') == "1"
    donors = get_all_donors(admin_view=admin)
    return jsonify(donors), 200

@app.route('/donor', methods=['POST'])
def create_donor():
    data = request.json
    donor_id = add_donor(
        name=data['name'],
        blood_type=data['blood_type'],
        hospital_id=data['hospital_id'],
        eligibility_status=data.get('eligibility_status', 'Eligible')
    )
    return jsonify({"donor_id": donor_id}), 201

@app.route('/donor/<int:donor_id>/eligibility', methods=['PUT'])
def set_donor_eligibility(donor_id):
    data = request.json
    updated = update_donor_eligibility(donor_id, data['eligibility_status'])
    return jsonify({"updated": updated}), 200

@app.route('/donor/<int:donor_id>', methods=['DELETE'])
def remove_donor(donor_id):
    deleted = delete_donor(donor_id)
    return jsonify({"deleted": deleted}), 200


if __name__ == '__main__':
    app.run(debug=True)