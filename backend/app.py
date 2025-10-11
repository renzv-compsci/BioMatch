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
    search_blood_across_hospitals
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
# TEST ENDPOINT
# =============================================

@app.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "pong"}), 200


if __name__ == '__main__':
    app.run(debug=True)