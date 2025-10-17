from flask import Blueprint, jsonify

from database.hospital import (
    get_all_hospitals,
    get_hospital_by_id,
    get_pending_requests_count
)
from database.donation import get_donations_by_hospital
from database.inventory import get_inventory_by_hospital

hospitals_bp = Blueprint('hospitals', __name__)


@hospitals_bp.route('/hospitals', methods=['GET'])
def get_hospitals():
    """Get all registered hospitals"""
    try:
        hospitals = get_all_hospitals()
        # Expand hospital data with full details
        detailed_hospitals = []
        for hospital in hospitals:
            full_data = get_hospital_by_id(hospital['id'])
            if full_data:
                detailed_hospitals.append(full_data)
        return jsonify(detailed_hospitals), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@hospitals_bp.route('/hospitals/<int:hospital_id>', methods=['GET'])
def get_hospital_details(hospital_id):
    """Get detailed hospital information with statistics"""
    try:
        hospital = get_hospital_by_id(hospital_id)
        if not hospital:
            return jsonify({'success': False, 'message': 'Hospital not found'}), 404
        
        # Get additional statistics
        hospital['pending_requests'] = get_pending_requests_count(hospital_id)
        
        # Get donations count
        donations = get_donations_by_hospital(hospital_id)
        hospital['total_donations'] = len(donations)
        
        # Get blood units available
        inventory = get_inventory_by_hospital(hospital_id)
        hospital['blood_units_available'] = sum(item.get('units_available', 0) for item in inventory)
        
        return jsonify(hospital), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@hospitals_bp.route('/hospitals/<int:hospital_id>/statistics', methods=['GET'])
def get_hospital_statistics(hospital_id):
    """Get comprehensive statistics for a hospital"""
    try:
        hospital = get_hospital_by_id(hospital_id)
        if not hospital:
            return jsonify({'success': False, 'message': 'Hospital not found'}), 404
        
        # Get pending requests
        pending_requests = get_pending_requests_count(hospital_id)
        
        # Get donations
        donations = get_donations_by_hospital(hospital_id)
        total_donations = len(donations)
        
        # Get inventory
        inventory = get_inventory_by_hospital(hospital_id)
        blood_units = sum(item.get('units_available', 0) for item in inventory)
        
        statistics = {
            'hospital_id': hospital_id,
            'hospital_name': hospital.get('name'),
            'pending_requests': pending_requests,
            'total_donations': total_donations,
            'blood_units_available': blood_units,
            'inventory_breakdown': inventory
        }
        
        return jsonify(statistics), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
