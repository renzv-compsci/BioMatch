from flask import Blueprint, request, jsonify
from database.hospital import (
    authenticate_hospital,
    get_hospital_by_id,
    update_hospital_password,
    get_blood_requests_by_hospital,
    get_pending_requests_count
)
from database.donation import get_donations_by_hospital
from database.inventory import get_inventory_by_hospital

hospital_auth_bp = Blueprint('hospital_auth', __name__)


@hospital_auth_bp.route('/hospital/login', methods=['POST'])
def hospital_login():
    """Authenticate hospital for portal access"""
    try:
        data = request.json
        hospital_id = data.get('hospital_id')
        password = data.get('password')
        
        if not hospital_id or not password:
            return jsonify({
                'success': False,
                'message': 'Hospital ID and password are required'
            }), 400
        
        hospital = authenticate_hospital(hospital_id, password)
        
        if not hospital:
            return jsonify({
                'success': False,
                'message': 'Invalid hospital ID or password'
            }), 401
        
        return jsonify({
            'success': True,
            'message': 'Hospital login successful',
            'hospital': {
                'id': hospital['id'],
                'name': hospital['name'],
                'address': hospital['address'],
                'contact_person': hospital['contact_person'],
                'contact_number': hospital['contact_number']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@hospital_auth_bp.route('/hospital/<int:hospital_id>/change-password', methods=['POST'])
def change_hospital_password(hospital_id):
    """Change hospital password"""
    try:
        data = request.json
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Old and new passwords are required'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'New password must be at least 6 characters'
            }), 400
        
        if update_hospital_password(hospital_id, old_password, new_password):
            return jsonify({
                'success': True,
                'message': 'Password updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Old password is incorrect'
            }), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@hospital_auth_bp.route('/hospital/<int:hospital_id>/dashboard', methods=['GET'])
def hospital_dashboard(hospital_id):
    """Get hospital dashboard data"""
    try:
        hospital = get_hospital_by_id(hospital_id)
        if not hospital:
            return jsonify({'success': False, 'message': 'Hospital not found'}), 404
        
        # Get requests
        requests_data = get_blood_requests_by_hospital(hospital_id)
        pending_requests = len([r for r in requests_data if r.get('status') == 'pending'])
        
        # Get donations
        donations = get_donations_by_hospital(hospital_id)
        
        # Get inventory
        inventory = get_inventory_by_hospital(hospital_id)
        blood_units = sum(item.get('units_available', 0) for item in inventory)
        
        return jsonify({
            'success': True,
            'hospital': {
                'id': hospital['id'],
                'name': hospital['name'],
                'address': hospital['address'],
                'contact_person': hospital['contact_person'],
                'contact_number': hospital['contact_number']
            },
            'statistics': {
                'pending_requests': pending_requests,
                'total_requests': len(requests_data),
                'total_donations': len(donations),
                'blood_units_available': blood_units,
                'inventory': inventory
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@hospital_auth_bp.route('/hospital/<int:hospital_id>/requests', methods=['GET'])
def get_hospital_requests(hospital_id):
    """Get all blood requests for a hospital"""
    try:
        requests_data = get_blood_requests_by_hospital(hospital_id)
        return jsonify({
            'success': True,
            'count': len(requests_data),
            'requests': requests_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@hospital_auth_bp.route('/hospital/<int:hospital_id>/donations', methods=['GET'])
def get_hospital_donations(hospital_id):
    """Get all donations from a hospital"""
    try:
        donations = get_donations_by_hospital(hospital_id)
        return jsonify({
            'success': True,
            'count': len(donations),
            'donations': donations
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
