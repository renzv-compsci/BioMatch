from flask import Flask, request, jsonify
from flask import Flask, jsonify

from database import (
    initialize_db,
    create_user,
    authenticate_user,
    add_hospital,
    get_all_hospital,
    get_hospital
)

app = Flask(__name__)

# initialize database at start up
initialize_db()

@app.route('/')
def home():
    return jsonify({"message": "BioMatch Flask server is running!"})

@app.route('/ping')
def ping():
    return jsonify({"status": "ok", "message": "pong"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = authenticate_user (username, password)
    
    if user:
        return jsonify({
            "message": "Login successful",
            "username": user["username"],
            "role": user["role"],
            "hospital_id": user["hospital_id"]
        }), 200
    
    else: 
        return  jsonify({"message": "Invalid credentials"}), 401
    
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'hospital_staff')
    hospital_id = data.get('hospital_id')

    if not all ([username, password, role]):
        return jsonify({"message": "Missing required fields"}), 400
    created = create_user(username, password, role, hospital_id)

    if created: 
        return jsonify({"message": "User registered successfully."}), 201
    else: 
        return jsonify({"message": "Registration failed: Username may already exist."}), 409

@app.route('/hospitals', methods=['GET'])
def hospitals():
    hospitals = get_all_hospital()
    return jsonify(hospitals), 200

@app.route('/hospital/<name>', methods=['GET'])
def hospital_by_name(name):
    hospital = get_all_hospital()
    
    if hospital:
        return jsonify(hospital), 200
    else: 
        return jsonify ({"message": "Hospital not found"}), 404
    
@app.route('/hospital', methods=['POST'])
def add_hospital_route():
    data = request.json
    name = data.get('name')
    address = data.get('adress')
    location_x = data.get('location_x')
    location_y = data.get('location_y')

    if not all([name, address, location_x, location_y]):
        return jsonify({"message": "Missing required fields"}), 400
    created = add_hospital(name, address, float(location_x), float(location_y))
    if created:
        return jsonify({"message": "Hospital added successfully."}), 201
    else:
        return jsonify({"message": "Hospital already exists."}), 409
    
if __name__ == '__main__':
    app.run(debug=True)