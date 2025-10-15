"""
Test script for the Blood Request Feature
Tests all validation scenarios and expected responses
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def print_test_header(test_name):
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)

def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

# Test 1: Valid request (may have no results if database is empty)
print_test_header("Test 1: Valid Request")
payload = {
    "blood_type": "A+",
    "quantity_needed": 3,
    "priority_level": "High",
    "required_date": "2025-10-18"
}
response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
print_response(response)

# Test 2: Legacy endpoint route
print_test_header("Test 2: Legacy Route (/request_blood)")
response = requests.post(f"{BASE_URL}/request_blood", json=payload)
print_response(response)

# Test 3: Missing required field
print_test_header("Test 3: Missing Required Field (priority_level)")
payload = {
    "blood_type": "O+",
    "quantity_needed": 2,
    "required_date": "2025-10-20"
}
response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
print_response(response)

# Test 4: Invalid blood type
print_test_header("Test 4: Invalid Blood Type")
payload = {
    "blood_type": "XY+",
    "quantity_needed": 3,
    "priority_level": "High",
    "required_date": "2025-10-18"
}
response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
print_response(response)

# Test 5: Invalid quantity (negative)
print_test_header("Test 5: Invalid Quantity (Negative)")
payload = {
    "blood_type": "B+",
    "quantity_needed": -5,
    "priority_level": "Medium",
    "required_date": "2025-10-18"
}
response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
print_response(response)

# Test 6: Invalid quantity (zero)
print_test_header("Test 6: Invalid Quantity (Zero)")
payload = {
    "blood_type": "AB-",
    "quantity_needed": 0,
    "priority_level": "Critical",
    "required_date": "2025-10-18"
}
response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
print_response(response)

# Test 7: Invalid priority level
print_test_header("Test 7: Invalid Priority Level")
payload = {
    "blood_type": "O-",
    "quantity_needed": 10,
    "priority_level": "Super Urgent",
    "required_date": "2025-10-18"
}
response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
print_response(response)

# Test 8: Invalid date format
print_test_header("Test 8: Invalid Date Format")
payload = {
    "blood_type": "A-",
    "quantity_needed": 2,
    "priority_level": "Low",
    "required_date": "18-10-2025"  # Wrong format
}
response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
print_response(response)

# Test 9: Valid request with datetime format
print_test_header("Test 9: Valid Request with DateTime Format")
payload = {
    "blood_type": "O+",
    "quantity_needed": 5,
    "priority_level": "Critical",
    "required_date": "2025-10-18T14:30:00"
}
response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
print_response(response)

# Test 10: All blood types
print_test_header("Test 10: Test All Valid Blood Types")
blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
for blood_type in blood_types:
    payload = {
        "blood_type": blood_type,
        "quantity_needed": 1,
        "priority_level": "Medium",
        "required_date": "2025-10-18"
    }
    response = requests.post(f"{BASE_URL}/api/v1/blood/request", json=payload)
    print(f"{blood_type}: Status {response.status_code} - {response.json().get('message', 'N/A')}")

print("\n" + "="*70)
print("ALL TESTS COMPLETED")
print("="*70)
