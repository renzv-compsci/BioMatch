# Blood Request Feature - Summary

## What Was Implemented

A backend API endpoint that allows hospitals to request blood and get a list of available matching blood units across all hospitals.

---

## API Endpoint

**POST** `/api/v1/blood/request` (also available as `/request_blood`)

### Request
```json
{
  "blood_type": "A+",
  "quantity_needed": 3,
  "priority_level": "High",
  "required_date": "2025-10-18"
}
```

### Response (Success)
```json
{
  "message": "Found 2 hospital(s) with matching blood units",
  "requested": { ... },
  "results": [
    {
      "blood_type": "A+",
      "hospital_name": "City General Hospital",
      "units_available": 5
    }
  ]
}
```

### Response (No Results)
```json
{
  "message": "No matching blood units found for type A+",
  "requested": { ... },
  "results": []
}
```

### Response (Validation Error - 400)
```json
{
  "message": "Invalid blood type. Must be one of: A+, A-, B+, B-, AB+, AB-, O+, O-"
}
```

---

## Implementation

### 1. Database Function (`database.py`)
```python
def search_available_blood_units(blood_type, quantity_needed, priority_level):
    """Search for available blood units across all hospitals"""
    # SQL query joins inventory and hospitals tables
    # Filters for exact blood type match and units > 0
    # Sorts by units_available DESC, hospital_name ASC
    # Returns: [{"blood_type": "A+", "hospital_name": "...", "units_available": 5}]
```

### 2. API Endpoint (`app.py`)
- Validates all required fields (blood_type, quantity_needed, priority_level, required_date)
- Validates blood type is one of 8 valid types (A+, A-, B+, B-, AB+, AB-, O+, O-)
- Validates quantity is positive integer
- Validates priority is Low/Medium/High/Critical
- Validates date is ISO 8601 format
- Calls database function
- Returns JSON response with results

---

## Key Features

✅ Comprehensive input validation with clear error messages  
✅ Returns exact blood type matches only  
✅ Sorted by availability (highest first)  
✅ Proper HTTP status codes (200, 400)  
✅ Works with existing database schema  

---

## Testing

Run the test script:
```powershell
cd backend
python test_blood_request.py
```

Or test manually:
```powershell
$body = @{
    blood_type = 'A+'
    quantity_needed = 3
    priority_level = 'High'
    required_date = '2025-10-18'
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://localhost:5000/api/v1/blood/request' `
    -Method POST -Body $body -ContentType 'application/json'
```

---

## Files Modified

- `backend/app.py` - Added endpoint with validation
- `backend/database.py` - Added search function
- `backend/docu4endpoints.md` - Updated API documentation
- `backend/test_blood_request.py` - Test suite

**Branch:** feature/kira-ml
