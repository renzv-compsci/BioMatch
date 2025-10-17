# BioMatch - Blood Bank Management System

## Comprehensive Project Documentation

**Project Type:** Blood Bank Management System  
**Language:** Python 3.11+  
**Framework:** Flask (Backend) + Tkinter (Frontend)  
**Database:** SQLite3  
**Purpose:** DSA (Data Structures & Algorithms) Course Project

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Algorithms & Data Structures](#algorithms--data-structures)
4. [Hashing & Security](#hashing--security)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [User Flow](#user-flow)
8. [Features](#features)
9. [Installation & Setup](#installation--setup)

---

## Project Overview

### Purpose

BioMatch is a unified blood bank management portal that enables hospitals to:

- Manage blood inventory
- Send and receive blood requests between hospitals
- Track donations and transactions
- Search for available blood across the hospital network

### Key Objectives

- **DSA Implementation**: Showcase various algorithms (searching, sorting, filtering)
- **Security**: Implement password hashing using bcrypt
- **Database Management**: Efficient data storage and retrieval
- **Real-world Application**: Solve actual blood bank coordination problems

---

## System Architecture

### Architecture Pattern: **Client-Server with MVC**

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Tkinter)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   View       │  │  Controller  │  │    Model     │  │
│  │  (Pages)     │◄─┤   (main.py)  │─►│  (API calls) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Requests (JSON)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (Flask API)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Routes     │  │   Business   │  │   Database   │  │
│  │  (app.py)    │─►│    Logic     │─►│   (SQLite)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer           | Technology         | Purpose                         |
| --------------- | ------------------ | ------------------------------- |
| **Frontend**    | Tkinter            | Desktop GUI framework           |
| **Styling**     | ttk + Custom Theme | Modern UI components            |
| **Backend**     | Flask 3.0.3        | REST API server                 |
| **Database**    | SQLite3            | Lightweight relational database |
| **Security**    | bcrypt 4.0.1       | Password hashing                |
| **HTTP Client** | requests 2.32.3    | Frontend-backend communication  |
| **CORS**        | flask-cors         | Cross-origin resource sharing   |

---

## Algorithms & Data Structures

### 1. **Search Algorithms**

#### A. Blood Type Search (Linear Search)

**Location:** `backend/app.py` - `/search_blood`

**Algorithm:**

```python
def search_blood_across_hospitals(blood_type, units_needed):
    # Algorithm: Linear Search with filtering
    # Time Complexity: O(n) where n = number of hospitals
    # Space Complexity: O(m) where m = matching results

    results = []
    for hospital in all_hospitals:
        inventory = get_hospital_inventory(hospital_id)
        for blood_item in inventory:
            if blood_item.blood_type == target_blood_type:
                if blood_item.units >= units_needed:
                    results.append(blood_item)
    return results
```

**Use Case:** Finding hospitals with specific blood type and sufficient units

#### B. Hospital-Specific Data Filtering

**Location:** Multiple endpoints (`/blood_requests/<hospital_id>`, `/transactions/<hospital_id>`)

**Algorithm:**

```python
def get_requests_for_hospital(hospital_id):
    # Algorithm: Database Query with Index Filtering
    # Time Complexity: O(log n) with indexed hospital_id
    # Space Complexity: O(k) where k = matching records

    # SQL uses B-Tree index on hospital_id for fast lookup
    query = """
        SELECT * FROM blood_requests
        WHERE source_hospital_id = ? OR requesting_hospital_id = ?
        ORDER BY created_at DESC
    """
    return execute_query(query, [hospital_id, hospital_id])
```

**Use Case:** Filtering blood requests/transactions specific to each hospital

### 2. **Sorting Algorithms**

#### A. Request Prioritization (Quick Sort)

**Location:** `frontend/pages/hospital_blood_requests_page.py`

**Algorithm:**

```python
def sort_requests_by_priority(requests):
    # Algorithm: Multi-level Quick Sort
    # Time Complexity: O(n log n) average case
    # Space Complexity: O(log n) stack space

    priority_order = {'Emergency': 1, 'Urgent': 2, 'Normal': 3}

    return sorted(requests, key=lambda x: (
        priority_order.get(x['priority'], 999),  # Primary: Priority
        x['created_at']                           # Secondary: Time
    ))
```

**Use Case:** Displaying blood requests in order of urgency

#### B. Transaction History Sorting

**Location:** Backend SQL queries

**Algorithm:**

```sql
-- Algorithm: Database Merge Sort (built-in ORDER BY)
-- Time Complexity: O(n log n)
SELECT * FROM transactions
WHERE hospital_id = ?
ORDER BY created_at DESC
LIMIT 100
```

**Use Case:** Showing most recent transactions first

### 3. **Data Structures**

#### A. Hash Tables (Dictionaries)

**Usage:** Caching and quick lookup

```python
# Hospital inventory cache
inventory_cache = {
    'hospital_1': {'A+': 50, 'B+': 30, 'O+': 100},
    'hospital_2': {'A+': 25, 'AB-': 10, 'O-': 15}
}
# Time Complexity: O(1) average case for lookup
```

#### B. Lists (Arrays)

**Usage:** Storing collections of records

```python
# Blood requests list
requests = [
    {'id': 1, 'blood_type': 'A+', 'units': 2},
    {'id': 2, 'blood_type': 'O-', 'units': 5}
]
# Time Complexity: O(n) for iteration, O(1) for append
```

#### C. Queue (FIFO)

**Usage:** Processing blood requests

```python
from collections import deque

pending_requests = deque()
pending_requests.append(new_request)  # Enqueue
processed = pending_requests.popleft()  # Dequeue
# Time Complexity: O(1) for both operations
```

#### D. Binary Tree (Database B-Tree)

**Usage:** SQLite indexing

```sql
CREATE INDEX idx_hospital_id ON blood_requests(source_hospital_id);
CREATE INDEX idx_blood_type ON inventory(blood_type);
-- Lookup Time Complexity: O(log n)
```

### 4. **String Matching Algorithms**

#### Pattern Matching for Blood Type Validation

**Location:** `frontend/pages/base_page.py` - `perform_search()`

```python
def validate_blood_type(input_str):
    # Algorithm: Exact String Matching
    # Time Complexity: O(1) with set lookup
    # Space Complexity: O(1)

    valid_types = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    return input_str.upper() in valid_types
```

---

## Hashing & Security

### Password Hashing with bcrypt

#### Algorithm: **bcrypt (Blowfish cipher-based)**

**Key Features:**

- **Salt:** Automatically generated random salt
- **Cost Factor:** Configurable work factor (default: 12)
- **Rainbow Table Resistant:** Each password hash is unique due to salt
- **Slow by Design:** Prevents brute-force attacks

#### Implementation

**Location:** `backend/database/user.py`

```python
import bcrypt

def hash_password(plain_password):
    """
    Algorithm: bcrypt adaptive hashing

    Steps:
    1. Generate random salt (128 bits)
    2. Combine salt with password
    3. Apply Blowfish encryption (2^12 rounds by default)
    4. Return hash string with salt embedded

    Format: $2b$12$[22-char salt][31-char hash]

    Time Complexity: Intentionally slow (~100-300ms)
    Security: Resistant to:
        - Rainbow tables (unique salt)
        - Brute force (slow computation)
        - GPU attacks (memory-hard)
    """
    salt = bcrypt.gensalt()  # Generate random salt
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password, hashed_password):
    """
    Algorithm: bcrypt verification

    Steps:
    1. Extract salt from stored hash
    2. Hash provided password with extracted salt
    3. Compare resulting hash with stored hash
    4. Return True if match, False otherwise

    Time Complexity: Same as hashing (~100-300ms)
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

#### Security Benefits

| Attack Type           | Protection Mechanism                     |
| --------------------- | ---------------------------------------- |
| **Rainbow Tables**    | Unique salt per password                 |
| **Brute Force**       | Slow hash function (adjustable cost)     |
| **Dictionary Attack** | Work factor makes each attempt expensive |
| **GPU Acceleration**  | Memory-hard algorithm                    |
| **Timing Attacks**    | Constant-time comparison                 |

#### Example Hash

```
Input:    "hospital123"
Salt:     $2b$12$N9qo8uLOickgx2ZMRZoMye
Hash:     $2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
          └─┘ └─┘ └────────────────────┘ └──────────────────────────┘
           │   │           │                        │
      Algorithm│      Salt (22 chars)        Hash (31 chars)
            Work Factor
```

### Database Security

#### SQL Injection Prevention

**Method:** Parameterized queries

```python
# ✓ SAFE - Parameterized query
cursor.execute(
    "SELECT * FROM hospitals WHERE id = ?",
    (hospital_id,)
)

# ✗ UNSAFE - String concatenation (vulnerable)
cursor.execute(
    f"SELECT * FROM hospitals WHERE id = {hospital_id}"
)
```

#### Session Management

- **Token-based**: Pseudo-user objects for authentication
- **Stateless**: No server-side session storage
- **Client-side**: Current user stored in frontend controller

---

## Database Schema

### Entity-Relationship Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  hospitals   │◄────────┤    users     │         │  donations   │
│              │ 1     * │              │         │              │
│ id (PK)      │         │ id (PK)      │    ┌────┤ id (PK)      │
│ name         │         │ username     │    │    │ donor_name   │
│ address      │         │ password_hash│    │    │ blood_type   │
│ contact_person│        │ hospital_id(FK)│   │    │ units        │
│ contact_number│        │ role         │    │    │ hospital_id(FK)│
│ password     │         └──────────────┘    │    │ date         │
└──────┬───────┘                             │    └──────────────┘
       │                                     │
       │ 1                                   │ *
       │                                     │
       ▼                                     │
┌──────────────┐         ┌──────────────┐   │    ┌──────────────┐
│  inventory   │         │blood_requests│   │    │ transactions │
│              │         │              │   │    │              │
│ id (PK)      │         │ id (PK)      │   │    │ id (PK)      │
│ blood_type   │         │ requesting_  │◄──┘    │ type         │
│ units_available│       │   hospital_id│        │ blood_type   │
│ hospital_id(FK)│       │ source_      │        │ units        │
│ last_updated │         │   hospital_id│        │ hospital_id(FK)│
└──────────────┘         │ blood_type   │        │ status       │
                         │ units_requested│      │ created_at   │
                         │ patient_name │        └──────────────┘
                         │ status       │
                         │ priority     │
                         └──────────────┘
```

### Table Definitions

#### 1. **hospitals**

Primary entity representing blood banks/hospitals

| Column         | Type      | Constraints               | Description                              |
| -------------- | --------- | ------------------------- | ---------------------------------------- |
| id             | INTEGER   | PRIMARY KEY AUTOINCREMENT | Unique hospital ID                       |
| name           | TEXT      | UNIQUE NOT NULL           | Hospital name                            |
| address        | TEXT      | NOT NULL                  | Physical address                         |
| contact_person | TEXT      | NOT NULL                  | Primary contact                          |
| contact_number | TEXT      | NOT NULL                  | Phone number                             |
| password       | TEXT      | DEFAULT 'hospital123'     | Portal password (plain - will be hashed) |
| created_at     | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration date                        |

**Indexes:** None (small table, ID is primary key)

#### 2. **users** (Legacy - will be removed)

User accounts under hospitals

| Column        | Type    | Constraints                 | Description     |
| ------------- | ------- | --------------------------- | --------------- |
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT   | User ID         |
| username      | TEXT    | UNIQUE NOT NULL             | Login username  |
| password_hash | TEXT    | NOT NULL                    | bcrypt hash     |
| role          | TEXT    | DEFAULT 'staff'             | User role       |
| hospital_id   | INTEGER | FOREIGN KEY → hospitals(id) | Linked hospital |

**Indexes:** `CREATE INDEX idx_username ON users(username)`

#### 3. **inventory**

Current blood stock per hospital

| Column          | Type      | Constraints                 | Description               |
| --------------- | --------- | --------------------------- | ------------------------- |
| id              | INTEGER   | PRIMARY KEY AUTOINCREMENT   | Record ID                 |
| blood_type      | TEXT      | NOT NULL                    | Blood type (A+, O-, etc.) |
| units_available | INTEGER   | DEFAULT 0                   | Current stock             |
| last_updated    | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP   | Last modification         |
| hospital_id     | INTEGER   | FOREIGN KEY → hospitals(id) | Owner hospital            |

**Unique Constraint:** `UNIQUE(blood_type, hospital_id)` - One record per blood type per hospital  
**Indexes:**

- `CREATE INDEX idx_blood_type ON inventory(blood_type)`
- `CREATE INDEX idx_hospital_inventory ON inventory(hospital_id, blood_type)`

#### 4. **donations**

Record of blood donations

| Column      | Type      | Constraints                 | Description        |
| ----------- | --------- | --------------------------- | ------------------ |
| id          | INTEGER   | PRIMARY KEY AUTOINCREMENT   | Donation ID        |
| donor_name  | TEXT      | NOT NULL                    | Donor's name       |
| blood_type  | TEXT      | NOT NULL                    | Donated blood type |
| units       | INTEGER   | NOT NULL                    | Number of units    |
| date        | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP   | Donation date      |
| hospital_id | INTEGER   | FOREIGN KEY → hospitals(id) | Receiving hospital |

**Indexes:** `CREATE INDEX idx_hospital_donations ON donations(hospital_id, date DESC)`

#### 5. **blood_requests**

Requests from one hospital to another

| Column                 | Type      | Constraints                 | Description               |
| ---------------------- | --------- | --------------------------- | ------------------------- |
| id                     | INTEGER   | PRIMARY KEY AUTOINCREMENT   | Request ID                |
| requesting_hospital_id | INTEGER   | FOREIGN KEY → hospitals(id) | Hospital requesting blood |
| source_hospital_id     | INTEGER   | FOREIGN KEY → hospitals(id) | Hospital providing blood  |
| blood_type             | TEXT      | NOT NULL                    | Requested blood type      |
| units_requested        | INTEGER   | NOT NULL                    | Number of units needed    |
| patient_name           | TEXT      | NOT NULL                    | Patient receiving blood   |
| patient_id             | TEXT      | NOT NULL                    | Patient ID/Medical record |
| requesting_doctor      | TEXT      | NOT NULL                    | Doctor making request     |
| priority               | TEXT      | DEFAULT 'Normal'            | Normal/Urgent/Emergency   |
| purpose                | TEXT      | -                           | Medical reason            |
| status                 | TEXT      | DEFAULT 'pending'           | pending/approved/rejected |
| notes                  | TEXT      | DEFAULT ''                  | Additional notes          |
| created_at             | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP   | Request creation time     |
| updated_at             | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP   | Last status update        |

**Indexes:**

- `CREATE INDEX idx_source_hospital ON blood_requests(source_hospital_id, status)`
- `CREATE INDEX idx_requesting_hospital ON blood_requests(requesting_hospital_id, status)`

**Business Logic:**

- Hospital A (requesting) sends request to Hospital B (source)
- Hospital B sees request in their "Blood Requests" page
- Hospital B can approve/reject
- On approval, both hospitals' transaction history is updated

#### 6. **transactions**

All blood-related operations

| Column             | Type      | Constraints                 | Description                  |
| ------------------ | --------- | --------------------------- | ---------------------------- |
| id                 | INTEGER   | PRIMARY KEY AUTOINCREMENT   | Transaction ID               |
| transaction_type   | TEXT      | NOT NULL                    | donation/request/transfer    |
| blood_type         | TEXT      | NOT NULL                    | Blood type involved          |
| units              | INTEGER   | NOT NULL                    | Number of units              |
| hospital_id        | INTEGER   | FOREIGN KEY → hospitals(id) | Primary hospital             |
| target_hospital_id | INTEGER   | FOREIGN KEY → hospitals(id) | Other hospital (if transfer) |
| status             | TEXT      | DEFAULT 'completed'         | completed/pending/cancelled  |
| priority_level     | TEXT      | -                           | Priority classification      |
| notes              | TEXT      | -                           | Transaction notes            |
| created_at         | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP   | Transaction time             |
| updated_at         | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP   | Last update                  |

**Indexes:** `CREATE INDEX idx_hospital_transactions ON transactions(hospital_id, created_at DESC)`

---

## API Endpoints

### Base URL

```
http://127.0.0.1:5000
```

### Authentication Endpoints

#### POST `/hospital/login`

**Description:** Hospital portal authentication

**Request Body:**

```json
{
  "hospital_id": 1,
  "password": "hospital123"
}
```

**Response (200 OK):**

```json
{
  "message": "Login successful",
  "hospital": {
    "id": 1,
    "name": "General Hospital",
    "address": "123 Main St",
    "contact_person": "Dr. Smith",
    "contact_number": "555-1234"
  }
}
```

**Algorithm:** Password verification using bcrypt

### Hospital Management

#### POST `/register_hospital`

**Description:** Register new hospital (creates hospital + admin user)

**Request Body:**

```json
{
  "name": "City General Hospital",
  "address": "456 Healthcare Ave",
  "contact_person": "Dr. Jane Doe",
  "contact_number": "555-9876",
  "password": "securepass123"
}
```

**Response (201 Created):**

```json
{
  "message": "Hospital registered successfully",
  "hospital_id": 3
}
```

#### GET `/hospitals`

**Description:** List all registered hospitals

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "name": "General Hospital",
    "address": "123 Main St",
    "contact_person": "Dr. Smith",
    "contact_number": "555-1234"
  },
  ...
]
```

**Algorithm:** Simple SELECT query with no filtering

### Blood Inventory

#### GET `/inventory/<hospital_id>`

**Description:** Get blood inventory for specific hospital

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "blood_type": "A+",
    "units_available": 50,
    "last_updated": "2025-10-17 14:30:00"
  },
  {
    "id": 2,
    "blood_type": "O-",
    "units_available": 25,
    "last_updated": "2025-10-17 12:15:00"
  }
]
```

**Algorithm:** Database query filtered by hospital_id (O(log n) with index)

#### POST `/add_donation`

**Description:** Add blood donation (updates inventory)

**Request Body:**

```json
{
  "donor_name": "John Smith",
  "blood_type": "A+",
  "units": 2,
  "hospital_id": 1
}
```

**Response (201 Created):**

```json
{
  "message": "Donation added successfully",
  "donation_id": 45
}
```

**Algorithm:**

1. Insert into donations table
2. Update inventory (increment units) for matching blood type
3. Create transaction record

### Blood Search

#### POST `/search_blood`

**Description:** Search for hospitals with specific blood type

**Request Body:**

```json
{
  "blood_type": "AB+",
  "units_needed": 2
}
```

**Response (200 OK):**

```json
[
  {
    "hospital_id": 2,
    "hospital_name": "City Medical Center",
    "blood_type": "AB+",
    "units_available": 10,
    "address": "789 Medical Plaza",
    "contact_number": "555-4567"
  },
  {
    "hospital_id": 4,
    "hospital_name": "Regional Hospital",
    "blood_type": "AB+",
    "units_available": 5,
    "address": "321 Hospital Rd",
    "contact_number": "555-8901"
  }
]
```

**Algorithm:**

```python
# Linear search across all hospitals
for each hospital in hospitals:
    inventory = get_inventory(hospital.id)
    for item in inventory:
        if item.blood_type == search_blood_type:
            if item.units >= units_needed:
                results.append({hospital, item})
return results
```

**Time Complexity:** O(h × i) where h = hospitals, i = inventory items per hospital

### Blood Requests

#### POST `/blood_requests/create`

**Description:** Send blood request from one hospital to another

**Request Body:**

```json
{
  "requesting_hospital_id": 2,
  "source_hospital_id": 4,
  "blood_type": "AB+",
  "units_requested": 2,
  "patient_name": "Jane Doe",
  "patient_id": "P12345",
  "requesting_doctor": "Dr. Brown",
  "priority": "Urgent",
  "purpose": "Emergency surgery"
}
```

**Response (201 Created):**

```json
{
  "message": "Blood request sent successfully",
  "request_id": 78
}
```

**Algorithm:**

1. Validate both hospital IDs exist
2. Insert into blood_requests table
3. Set status = 'pending'

#### GET `/blood_requests/<hospital_id>`

**Description:** Get all blood requests involving a hospital (as sender or receiver)

**Response (200 OK):**

```json
[
  {
    "id": 78,
    "requesting_hospital_id": 2,
    "requesting_hospital_name": "City Medical",
    "source_hospital_id": 4,
    "source_hospital_name": "Regional Hospital",
    "blood_type": "AB+",
    "units_requested": 2,
    "patient_name": "Jane Doe",
    "priority": "Urgent",
    "status": "pending",
    "created_at": "2025-10-17 15:45:00"
  }
]
```

**Algorithm:**

```sql
SELECT * FROM blood_requests
WHERE source_hospital_id = ? OR requesting_hospital_id = ?
ORDER BY created_at DESC
```

**Time Complexity:** O(log n) with composite index on (source_hospital_id, status)

#### PUT `/blood_requests/<request_id>/approve`

**Description:** Approve blood request (source hospital action)

**Response (200 OK):**

```json
{
  "message": "Request approved",
  "transaction_id": 123
}
```

**Algorithm:**

1. Update blood_requests.status = 'approved'
2. Deduct units from source hospital inventory
3. Add units to requesting hospital inventory
4. Create transaction record for both hospitals
5. Update blood_requests.updated_at

#### PUT `/blood_requests/<request_id>/reject`

**Description:** Reject blood request

**Response (200 OK):**

```json
{
  "message": "Request rejected"
}
```

**Algorithm:**

1. Update blood_requests.status = 'rejected'
2. Update blood_requests.updated_at
3. Optionally add rejection notes

### Transaction History

#### GET `/transactions/<hospital_id>`

**Description:** Get transaction history for hospital

**Query Parameters:**

- `limit`: Number of records (default: 100)
- `type`: Filter by transaction_type
- `status`: Filter by status

**Response (200 OK):**

```json
[
  {
    "id": 123,
    "transaction_type": "transfer",
    "blood_type": "AB+",
    "units": 2,
    "status": "completed",
    "created_at": "2025-10-17 16:00:00",
    "hospital_name": "City Medical",
    "notes": "Emergency transfer to Regional Hospital"
  }
]
```

**Algorithm:**

```sql
SELECT * FROM transactions
WHERE hospital_id = ?
  AND (? IS NULL OR transaction_type = ?)
  AND (? IS NULL OR status = ?)
ORDER BY created_at DESC
LIMIT ?
```

---

## User Flow

### 1. Hospital Registration Flow

```
┌──────────────┐
│   Welcome    │
│    Page      │
└──────┬───────┘
       │ Click "Register Hospital"
       ▼
┌──────────────────────────────────┐
│   Register Hospital Page          │
│                                   │
│  [Hospital Name          ]        │
│  [Address                ]        │
│  [Contact Person         ]        │
│  [Contact Number         ]        │
│  [Password (default shown)]       │
│                                   │
│       [Register Button]           │
└──────┬──────────────────────────┘
       │ POST /register_hospital
       ▼
┌──────────────────────────────────┐
│   Backend Processing              │
│  1. Validate input               │
│  2. Hash password (bcrypt)       │
│  3. Insert into hospitals table  │
│  4. Initialize inventory         │
│     (all blood types, 0 units)   │
│  5. Return hospital_id           │
└──────┬──────────────────────────┘
       │ Success
       ▼
┌──────────────┐
│  Login Page  │
│              │
│  "Hospital   │
│  registered! │
│  Please      │
│  login"      │
└──────────────┘
```

### 2. Login Flow

```
┌──────────────┐
│  Login Page  │
│              │
│  [Hospital ID    ]               │
│  [Password       ]               │
│  [💡 Default: hospital123]       │
│                                  │
│       [Login Button]             │
└──────┬──────────────────────────┘
       │ POST /hospital/login
       ▼
┌──────────────────────────────────┐
│   Backend Authentication          │
│  1. Get hospital by ID           │
│  2. Verify password (bcrypt)     │
│  3. Return hospital data         │
└──────┬──────────────────────────┘
       │ Success
       ▼
┌──────────────────────────────────┐
│   Frontend Controller             │
│  1. Store hospital data          │
│  2. Create pseudo-user object    │
│  3. Navigate to Dashboard        │
└──────┬──────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│   Unified Dashboard               │
│  ┌────────────────────────────┐  │
│  │ Header: Search | User Info │  │
│  └────────────────────────────┘  │
│  ┌───────┬──────────────────────┐│
│  │ Side  │ Main Content         ││
│  │ bar   │                      ││
│  │       │  📊 Stats            ││
│  │ 📊    │  🩸 Inventory        ││
│  │ 🩸    │  💉 Add Donation     ││
│  │ 📋    │                      ││
│  │ 📜    │                      ││
│  │ 🚪    │                      ││
│  └───────┴──────────────────────┘│
└──────────────────────────────────┘
```

### 3. Blood Request Flow (Hospital A → Hospital B)

```
┌─────────────────────────────────────────┐
│   Hospital A (Requesting Hospital)      │
│                                         │
│   1. Need AB+ blood (2 units)          │
│   2. Search in header search bar       │
└─────┬───────────────────────────────────┘
      │ POST /search_blood
      ▼
┌─────────────────────────────────────────┐
│   Search Results Popup                   │
│  ┌───────────────────────────────────┐  │
│  │ Hospital  | Blood | Units | Action│  │
│  ├───────────────────────────────────┤  │
│  │ Hospital B│ AB+   │ 10    │➤Request│  │
│  │ Hospital D│ AB+   │ 5     │➤Request│  │
│  └───────────────────────────────────┘  │
│  Double-click Hospital B                │
└─────┬───────────────────────────────────┘
      │ Opens Request Form
      ▼
┌─────────────────────────────────────────┐
│   Request Form (to Hospital B)           │
│  Blood Type: AB+ (pre-filled)           │
│  Units: [2]                             │
│  Patient: [Jane Doe]                    │
│  Patient ID: [P12345]                   │
│  Doctor: [Dr. Smith]                    │
│  Priority: [Urgent ▼]                   │
│  Purpose: [Emergency surgery...]        │
│                                         │
│       [✓ Send Request]                  │
└─────┬───────────────────────────────────┘
      │ POST /blood_requests/create
      ▼
┌─────────────────────────────────────────┐
│   Backend Processing                     │
│  1. Validate hospital IDs               │
│  2. Insert blood_request record:        │
│     - requesting_hospital_id: A         │
│     - source_hospital_id: B             │
│     - status: 'pending'                 │
└─────┬───────────────────────────────────┘
      │
      ├──────────────┬─────────────────────┐
      │              │                     │
      ▼              ▼                     ▼
┌───────────┐  ┌───────────┐      ┌──────────┐
│Hospital A │  │Hospital B │      │Hospital C│
│Dashboard  │  │Dashboard  │      │Dashboard │
│           │  │           │      │          │
│ (no change)  │📋 Blood   │      │(no change)│
│           │  │Requests:  │      │          │
│           │  │           │      │          │
│           │  │➤ New      │      │          │
│           │  │  request  │      │          │
│           │  │  from     │      │          │
│           │  │  Hospital│      │          │
│           │  │  A        │      │          │
└───────────┘  └─────┬─────┘      └──────────┘
                     │
                     │ Hospital B admin reviews
                     ▼
             ┌───────────────┐
             │  Approve or   │
             │  Reject?      │
             └───┬───────┬───┘
                 │       │
        ┌────────┘       └────────┐
        │ Approve                 │ Reject
        ▼                         ▼
┌───────────────────┐     ┌──────────────┐
│  PUT /blood_      │     │ PUT /blood_  │
│  requests/78/     │     │ requests/78/ │
│  approve          │     │ reject       │
└───────┬───────────┘     └──────┬───────┘
        │                        │
        ▼                        ▼
┌───────────────────┐     ┌──────────────┐
│ Backend:          │     │ Backend:     │
│ 1. Update status  │     │ 1. Update    │
│ 2. Hospital B:    │     │    status    │
│    AB+ -= 2       │     │ 2. No        │
│ 3. Hospital A:    │     │    inventory │
│    AB+ += 2       │     │    change    │
│ 4. Create         │     └──────────────┘
│    transactions   │
│    for both       │
└───────┬───────────┘
        │
        ▼
┌───────────────────────────────┐
│  Both hospitals see in        │
│  Transaction History:         │
│                               │
│  Hospital A:                  │
│  "Received 2 units AB+ from   │
│   Hospital B"                 │
│                               │
│  Hospital B:                  │
│  "Sent 2 units AB+ to         │
│   Hospital A"                 │
└───────────────────────────────┘
```

---

## Features

### 1. Dashboard (Unified Portal)

**Page:** `UnifiedDashboardPage`

**Components:**

- **Stats Cards**
  - Total Blood Units (sum of all inventory)
  - Pending Requests (count)
  - Total Requests (count)
- **Blood Inventory Table** (85% width)
  - Columns: Blood Type, Units Available, Last Updated
  - Height: 15 rows
  - Sortable by clicking headers
- **Quick Donation Form** (15% width)
  - Minimal compact design
  - Fields: Donor name, Blood type dropdown, Units
  - Button: "+ Add"
  - Recent donations list below

**Algorithms Used:**

- **Stats calculation**: O(n) aggregation
- **Inventory display**: O(1) retrieval with caching
- **Donation submission**: O(1) insert + O(1) inventory update

### 2. Request Blood (Sending Point)

**Page:** `BloodRequestPage`

**Purpose:** Hospital sends request to another hospital

**Flow:**

1. Fill patient details
2. Search available hospitals (via search or selection)
3. Submit request to selected hospital

**Algorithms:**

- **Hospital search**: Linear search O(n)
- **Request creation**: O(1) database insert

**Features:**

- Form validation
- Priority selection (Normal/Urgent/Emergency)
- Purpose/reason text area
- Recent requests table (sent by current hospital)

### 3. Blood Requests (Receiving Point)

**Page:** `HospitalBloodRequestsPage`

**Purpose:** Hospital views and manages incoming requests

**Flow:**

1. View requests FROM other hospitals TO current hospital
2. Filter by status/priority
3. Approve or reject requests

**Algorithms:**

- **Filtering**: SQL WHERE clause O(log n) with index
- **Approval processing**:
  - O(1) status update
  - O(1) inventory deduction (source)
  - O(1) inventory addition (requesting)
  - O(1) transaction creation (x2)

**Features:**

- Stats: Total, Pending, Approved, Rejected counts
- Create new request form
- Requests table with action buttons
- Approve/Reject functionality

### 4. Transaction History

**Page:** `TransactionHistoryPage`

**Purpose:** View all blood-related transactions

**Algorithms:**

- **Data retrieval**: O(log n) with date index
- **Filtering**: SQL query optimization
- **Sorting**: Database ORDER BY (Merge sort O(n log n))

**Features:**

- Filter by status (All/Pending/Approved/Rejected)
- Filter by priority
- Stats cards
- Detailed transaction table
- Add notes functionality

### 5. Global Blood Search

**Location:** Header search bar (all pages)

**Purpose:** Quick search across all hospitals

**Flow:**

1. Enter blood type (e.g., "AB+")
2. View results from all hospitals
3. Double-click to send request

**Algorithms:**

- **Search**: Linear scan O(h × i) where h=hospitals, i=inventory items
- **Result display**: O(m) where m=matching results

**Features:**

- Real-time validation
- Popup results window
- Direct request form access
- Hospital details included

### 6. Window Controls

**Location:** Header (all authenticated pages)

**Features:**

- **Maximize/Restore button**
  - Toggles between normal and maximized states
  - Updates button text dynamically
  - Uses `state('zoomed')` for Windows
- **Persistent state**: Remembers maximized state per session

---

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step 1: Clone Repository

```bash
git clone https://github.com/renzv-compsci/BioMatch.git
cd BioMatch
```

### Step 2: Install Dependencies

```bash
pip install -r backend/requirements.txt
```

**Required Packages:**

```
Flask==3.0.3
flask-cors==4.0.0
bcrypt==4.0.1
requests==2.32.3
Pillow==10.0.0
```

### Step 3: Initialize Database

```bash
cd backend
python database/db_init.py
```

**This creates:**

- `biomatch.db` file
- All required tables
- Sample data (optional)

### Step 4: Run Backend Server

```bash
# In backend directory
python app.py
```

**Server starts on:** `http://127.0.0.1:5000`

**Expected output:**

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
Database initialized!
```

### Step 5: Run Frontend Application

```bash
# In new terminal, from project root
python frontend/main.py
```

**Application launches:** Tkinter window opens with Welcome page

### Default Login Credentials

**Hospital ID:** 1, 2, 3, 4 (depending on registered hospitals)  
**Password:** `hospital123` (for all hospitals by default)

---

## Project Structure

```
BioMatch/
│
├── backend/
│   ├── app.py                    # Flask API server
│   ├── requirements.txt          # Python dependencies
│   ├── biomatch.db              # SQLite database (generated)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_init.py           # Database initialization
│   │   ├── hospital.py          # Hospital CRUD operations
│   │   ├── user.py              # User authentication (bcrypt)
│   │   ├── donation.py          # Donation management
│   │   ├── inventory.py         # Inventory operations
│   │   └── transaction.py       # Transaction logging
│   │
│   └── routes/
│       ├── blood_requests.py    # Blood request endpoints
│       ├── hospitals.py         # Hospital endpoints
│       └── hospital_auth.py     # Authentication endpoints
│
├── frontend/
│   ├── main.py                  # Main Tkinter application
│   ├── theme.py                 # UI theme and components
│   │
│   └── pages/
│       ├── __init__.py
│       ├── base_page.py         # Base class with header/sidebar
│       ├── welcome_page.py      # Landing page
│       ├── unified_login_page.py           # Single login
│       ├── register_hospital_page.py       # Hospital registration
│       ├── unified_dashboard_page.py       # Main dashboard
│       ├── blood_request_page.py           # Request blood form
│       ├── hospital_blood_requests_page.py # Manage incoming requests
│       └── transaction_history_page.py     # View transactions
│
├── md/
│   ├── HOW_TO_RUN.md            # Quick start guide
│   ├── BLOOD_REQUEST_UI.md      # UI documentation
│   └── TRANSACTION_HISTORY_FEATURE.md
│
├── PROJECT_DOCUMENTATION.md      # This file
├── README.md                     # Project overview
└── .gitignore
```

---

## Algorithm Complexity Analysis

### Time Complexity Summary

| Operation               | Algorithm                      | Best Case | Average Case | Worst Case | Space |
| ----------------------- | ------------------------------ | --------- | ------------ | ---------- | ----- |
| **Login**               | Password verification (bcrypt) | Ω(1)      | Θ(1)         | O(1)       | O(1)  |
| **Search Blood**        | Linear search                  | Ω(1)      | Θ(n)         | O(n)       | O(m)  |
| **Get Inventory**       | DB index lookup                | Ω(1)      | Θ(log n)     | O(log n)   | O(1)  |
| **Add Donation**        | DB insert + update             | Ω(1)      | Θ(1)         | O(1)       | O(1)  |
| **Get Requests**        | DB indexed query               | Ω(1)      | Θ(log n)     | O(log n)   | O(k)  |
| **Approve Request**     | Transaction processing         | Ω(1)      | Θ(1)         | O(1)       | O(1)  |
| **Sort Requests**       | Python sorted() (Timsort)      | Ω(n)      | Θ(n log n)   | O(n log n) | O(n)  |
| **Filter Transactions** | SQL WHERE + index              | Ω(1)      | Θ(log n)     | O(log n)   | O(k)  |

**Legend:**

- n = number of records
- m = number of matching results
- k = number of filtered results

### Space Complexity Summary

| Component            | Data Structure | Space Complexity |
| -------------------- | -------------- | ---------------- |
| **Inventory Cache**  | Dictionary     | O(h × b)         |
| **Request Queue**    | Deque          | O(r)             |
| **Search Results**   | List           | O(m)             |
| **Database Indexes** | B-Tree         | O(n log n)       |

**Legend:**

- h = number of hospitals
- b = number of blood types (constant: 8)
- r = number of pending requests
- m = search results
- n = table rows

---

## Conclusion

BioMatch demonstrates practical application of:

- **Data Structures**: Hash tables, lists, queues, B-trees
- **Algorithms**: Search (linear, binary via indexes), sorting (quick sort, merge sort)
- **Security**: bcrypt hashing, SQL injection prevention
- **Software Engineering**: MVC architecture, REST API design, database normalization

This project showcases how theoretical DSA concepts solve real-world problems in healthcare logistics.

---

**Last Updated:** October 17, 2025  
**Version:** 2.0  
**Authors:** Charles (with GitHub Copilot assistance)  
**Course:** Data Structures and Algorithms  
**Institution:** [Your University/Institution]

---

## References

1. **bcrypt Algorithm**: https://en.wikipedia.org/wiki/Bcrypt
2. **Flask Documentation**: https://flask.palletsprojects.com/
3. **SQLite B-Tree Implementation**: https://www.sqlite.org/btreemodule.html
4. **Python Timsort**: https://github.com/python/cpython/blob/main/Objects/listsort.txt
5. **RESTful API Design**: https://restfulapi.net/
