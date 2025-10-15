==================================================================================================================
||                             MADE BY YOURS TRULY, THE ONE AND ONLY, @PROJCJDEVS!                              ||
==================================================================================================================

## Documentation

## Overview
BioMatch is a hospital blood inventory management system built with Flask (backend), SQLite (database), and Tkinter (frontend). Hospitals can register, manage blood donations, track inventory, and search for compatible blood types across multiple institutions.

## Tech Stack
- **Backend:** Flask 3.0.3
- **Database:** SQLite (biomatch.db)
- **Password Security:** bcrypt 4.1.2
- **Frontend:** Tkinter (Python built-in)
- **CORS:** Flask-CORS 4.0.0

---

## Database Schema

### hospitals
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Unique identifier |
| name | TEXT (UNIQUE) | Hospital name |
| address | TEXT | Physical address |
| contact_person | TEXT | Contact name |
| contact_number | TEXT | Phone number |
| created_at | TIMESTAMP | Registration date |

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Unique identifier |
| username | TEXT (UNIQUE) | Login username |
| password_hash | TEXT | Bcrypt hashed password |
| role | TEXT | staff/nurse/doctor/admin |
| hospital_id | INTEGER (FK) | Links to hospitals |
| created_at | TIMESTAMP | Registration date |

### donations
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Unique identifier |
| donor_name | TEXT | Donor's name |
| blood_type | TEXT | A+, A-, B+, B-, AB+, AB-, O+, O- |
| units | INTEGER | Number of units |
| date | TIMESTAMP | Donation timestamp |
| hospital_id | INTEGER (FK) | Links to hospitals |

### inventory
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Unique identifier |
| blood_type | TEXT | Blood type |
| units_available | INTEGER | Current stock |
| last_updated | TIMESTAMP | Last modified |
| hospital_id | INTEGER (FK) | Links to hospitals |
| **UNIQUE** | (blood_type, hospital_id) | Prevents duplicates |

---

## API Endpoints

### `POST /register_hospital`
Register a new hospital and initialize inventory.

**Request:**
```json
{
  "name": "City Hospital",
  "address": "123 Main St",
  "contact_person": "Dr. Smith",
  "contact_number": "555-0100"
}

Response (201): {"message": "Hospital registered successfully", "hospital_id": 1}

GET /hospitals
Get all hospitals (for dropdown selection).

Response (200):
{
  "id": 1,
  "name": "City Hospital",
  "address": "123 Main St",
  "contact_person": "Dr. Smith",
  "contact_number": "555-0100"
}

POST /register
Register a user under a hospital.
{
  "username": "nurse_jane",
  "password": "password123",
  "role": "nurse",
  "hospital_id": 1
}

POST /login
Authenticate user and return session data.
{
  "username": "nurse_jane",
  "password": "password123"
}
Response (200):
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "nurse_jane",
    "role": "nurse",
    "hospital_id": 1
  }
}

POST /add_donation
Record donation and auto-update inventory.
{
  "donor_name": "John Doe",
  "blood_type": "O+",
  "units": 2,
  "hospital_id": 1
}


GET /donations/<hospital_id>
Get all donations for a hospital (newest first).
[
  {
    "id": 1,
    "donor_name": "John Doe",
    "blood_type": "O+",
    "units": 2,
    "date": "2023-10-11 14:30:00",
    "hospital_id": 1
  }
]


GET /inventory/<hospital_id>
Get current blood stock for a hospital.
[
  {"blood_type": "A+", "units_available": 20, "last_updated": "2023-10-11 14:30:00"},
  {"blood_type": "O-", "units_available": 5, "last_updated": "2023-10-10 10:00:00"}
]


POST /search_blood
Search for compatible blood across all hospitals.
{
  "blood_type": "AB+",
  "units_needed": 2
}
Response (200);
[
  {
    "blood_type": "O-",
    "units_available": 15,
    "hospital_name": "City Hospital",
    "address": "123 Main St",
    "contact_number": "555-0100"
  }
]

Blood Compatibility:

AB+ (universal receiver) → All types
AB- → A-, B-, AB-, O-
A+ → A+, A-, O+, O-
A- → A-, O-
B+ → B+, B-, O+, O-
B- → B-, O-
O+ → O+, O-
O- → O- only


---

## NEW FEATURE: Blood Request System

### `POST /request_blood` or `POST /api/v1/blood/request`
**Submit a blood request and retrieve matching available blood units across all hospitals.**

**Endpoint Choice Justification:**
- **Method:** `POST` (not GET)
- **Reason:** Complex request payload with multiple parameters, potential future logging/audit trail requirements, and follows RESTful best practices for resource queries with state implications.

**Request:**
```json
{
  "blood_type": "A+",
  "quantity_needed": 3,
  "priority_level": "High",
  "required_date": "2025-10-18"
}
```

**Field Validation:**
- `blood_type` (string, required): Must be one of: A+, A-, B+, B-, AB+, AB-, O+, O-
- `quantity_needed` (integer, required): Must be a positive integer
- `priority_level` (string, required): Must be one of: Low, Medium, High, Critical
- `required_date` (string, required): ISO 8601 date format (e.g., "2025-10-18" or "2025-10-18T14:30:00")

**Response (200 - Success with results):**
```json
{
  "message": "Found 2 hospital(s) with matching blood units",
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
    },
    {
      "blood_type": "A+",
      "hospital_name": "Metro Blood Center",
      "units_available": 2
    }
  ]
}
```

**Response (200 - No results found):**
```json
{
  "message": "No matching blood units found for type A+",
  "requested": {
    "blood_type": "A+",
    "quantity_needed": 3,
    "priority_level": "High",
    "required_date": "2025-10-18"
  },
  "results": []
}
```

**Response (400 - Validation Error):**
```json
{
  "message": "All fields are required: blood_type, quantity_needed, priority_level, required_date"
}
```

or

```json
{
  "message": "Invalid blood type. Must be one of: A+, A-, B+, B-, AB+, AB-, O+, O-"
}
```

**Data Flow:**
1. **Request Validation** → Validate all input parameters (blood type, quantity, priority, date)
2. **Database Query** → Query inventory table for exact blood type matches with units > 0
3. **Response Assembly** → Sort results by units available (DESC) and hospital name (ASC)
4. **Return JSON** → Return structured response with request context and results

**Key Features:**
- ✅ Comprehensive input validation with clear error messages
- ✅ Returns exact blood type matches only (no compatibility mapping)
- ✅ Results sorted by availability (highest to lowest)
- ✅ Includes request context in response for tracking
- ✅ RESTful status codes (200 for success/no results, 400 for validation errors)
- ✅ Supports both legacy `/request_blood` and versioned `/api/v1/blood/request` routes

---

GET /ping
Health check endpoint.

Response (200): {"status": "ok", "message": "pong"}



Frontend Pages (main_ui.py)
Page	                            Purpose
WelcomePage	Entry           point with navigation buttons
RegisterHospitalPage	    Form to register new hospital
RegisterUserPage	        Form to register user (with hospital dropdown)
LoginPage	                Username/password authentication
DashboardPage	            Shows stats (total units, donations) + navigation
AddDonationPage	            Form to record new donation
ViewInventoryPage	        Table showing current blood stock
SearchBloodPage	            Search compatible blood across hospitals

Testing Flow
Register a hospital → Get hospital_id
Register user → Select hospital from dropdown
Login → Access dashboard
Add donation → Inventory auto-updates
View inventory → See updated stock
Search blood → Find compatible types across hospitals
Security Features
Bcrypt password hashing with salt
Parameterized SQL queries (prevents injection)
Server-side input validation
Unique constraints on usernames/hospitals
CORS enabled for local development
Error Codes
200 - Success
201 - Created
400 - Bad Request (invalid input)
401 - Unauthorized (invalid credentials)
404 - Not Found
409 - Conflict (duplicate entry)
500 - Internal Server Error


==================================================================================================================
||                             MADE BY YOURS TRULY, THE ONE AND ONLY, @PROJCJDEVS!                              ||
==================================================================================================================