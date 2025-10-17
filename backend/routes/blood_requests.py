from flask import Blueprint, request, jsonify
from database.hospital import (
    create_blood_request, get_blood_requests_by_hospital, 
    get_blood_request_by_id, update_blood_request_status, 
    get_pending_requests_count, get_request_statistics
)

blood_request_bp = Blueprint('blood_requests', __name__)

@blood_request_bp.route('/requests', methods=['POST'])
def create_request():
    """API endpoint to create a new blood request"""
    data = request.json
    required_fields = ['requesting_hospital_id', 'source_hospital_id', 'blood_type', 
                       'units_requested', 'patient_name', 'patient_id', 
                       'requesting_doctor', 'priority', 'purpose']
    
    # Validate request data
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing field: {field}'}), 400
    
    request_id = create_blood_request(
        data['requesting_hospital_id'], data['source_hospital_id'], data['blood_type'],
        data['units_requested'], data['patient_name'], data['patient_id'],
        data['requesting_doctor'], data['priority'], data['purpose']
    )
    
    if request_id:
        return jsonify({'success': True, 'request_id': request_id}), 201
    else:
        return jsonify({'success': False, 'message': 'Failed to create blood request'}), 500


@blood_request_bp.route('/requests/hospital/<int:hospital_id>', methods=['GET'])
def get_requests_by_hospital(hospital_id):
    """API endpoint to get all blood requests for a hospital"""
    try:
        requests = get_blood_requests_by_hospital(hospital_id)
        return jsonify({'success': True, 'requests': requests}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@blood_request_bp.route('/requests/<int:request_id>', methods=['GET'])
def get_request_by_id(request_id):
    """API endpoint to get blood request details by ID"""
    try:
        request_details = get_blood_request_by_id(request_id)
        if request_details:
            return jsonify({'success': True, 'request': request_details}), 200
        else:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@blood_request_bp.route('/requests/<int:request_id>/status', methods=['PUT'])
def update_request_status(request_id):
    """API endpoint to update blood request status"""
    data = request.json
    if 'status' not in data:
        return jsonify({'success': False, 'message': 'Missing field: status'}), 400
    
    success = update_blood_request_status(request_id, data['status'])
    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to update request status'}), 500


@blood_request_bp.route('/requests/<int:hospital_id>/statistics', methods=['GET'])
def get_request_stats(hospital_id):
    """Get blood request statistics"""
    try:
        stats = get_request_statistics(hospital_id)
        return jsonify({'statistics': stats}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500