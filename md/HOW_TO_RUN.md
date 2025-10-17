# 🚀 How to Run BioMatch Software

## 📋 Prerequisites

Before running BioMatch, ensure you have:
- **Python 3.10+** installed on your system
- **Git** (optional, for version control)
- **Internet connection** (for first-time setup to install dependencies)

## 🔧 First-Time Setup

### Step 1: Install Backend Dependencies

Open PowerShell and navigate to the project directory:

```powershell
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch"
cd backend
pip install -r requirements.txt
```

**Required packages:**
- Flask 3.0.3 (Web framework)
- Flask-CORS 4.0.0 (Cross-origin support)
- requests 2.32.3 (HTTP library)
- bcrypt 4.0.1 (Password hashing)

### Step 2: Verify Database

The database (`biomatch.db`) should already exist in the `backend/` folder. If not, it will be automatically created when you first run the backend.

**Database location:** `C:\Users\Ken Ira Talingting\Documents\BioMatch\backend\biomatch.db`

---

## ▶️ Running the Software

### Method 1: Two Terminal Windows (Recommended)

#### Terminal 1 - Start Backend Server

```powershell
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\backend"
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**✅ Backend is ready when you see "Running on http://127.0.0.1:5000"**

#### Terminal 2 - Start Frontend Application

Open a **new PowerShell window**:

```powershell
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\frontend"
python main.py
```

**Expected result:**
- A fullscreen window appears with the BioMatch login screen

---

### Method 2: Background Backend (Alternative)

#### Step 1: Start Backend in Background

```powershell
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\backend"
Start-Process python -ArgumentList "app.py" -WindowStyle Hidden
```

#### Step 2: Start Frontend

```powershell
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\frontend"
python main.py
```

#### Step 3: Stop Background Backend (When Done)

```powershell
Get-Process python | Where-Object {$_.Path -like "*python*"} | Stop-Process -Force
```

---

## 🧪 Testing the Blood Request Feature

### Step 1: Login
- **Username:** `admin` (or any registered user)
- **Password:** Your password
- Click **"Login"**

### Step 2: Navigate to Blood Request
- Click **"Request Blood"** button on the dashboard

### Step 3: Fill the Form
- **Blood Type:** Select from dropdown (A+, A-, B+, B-, AB+, AB-, O+, O-)
- **Quantity Needed:** Enter number of units (positive integer)
- **Priority Level:** Select from dropdown (Critical, High, Medium, Low)
- **Required Date:** Select year, month, and day

### Step 4: Search Available Blood
- Click **"Search Available Blood"** button
- View results in the table below

### Step 5: Verify Results
- Results show: Hospital Name, Blood Type, Available Units, City

**Expected behavior:**
- ✅ Valid searches return HTTP 200 with results
- ✅ Invalid inputs show validation errors
- ✅ No 500 errors or crashes

---

## 🧪 Running Tests

### Backend API Tests

```powershell
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\backend"
python test_blood_request.py
```

**Expected output:**
```
..........
----------------------------------------------------------------------
Ran 10 tests in X.XXXs

OK
```

**All 10 tests should pass:**
1. ✅ Valid blood request
2. ✅ Missing required fields
3. ✅ Invalid blood type
4. ✅ Negative quantity
5. ✅ Invalid priority level
6. ✅ Invalid date format
7. ✅ Missing blood type
8. ✅ Missing quantity
9. ✅ Missing priority
10. ✅ Missing date

---

## ❌ Troubleshooting

### Problem: Backend won't start

**Error:** `Address already in use`

**Solution:**
```powershell
# Stop all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Try starting backend again
cd backend
python app.py
```

---

### Problem: Frontend shows connection error

**Error:** `Failed to connect to backend`

**Solution:**
1. Verify backend is running on `http://127.0.0.1:5000`
2. Check firewall isn't blocking port 5000
3. Restart backend server

---

### Problem: Database errors

**Error:** `sqlite3.OperationalError: no such table`

**Solution:**
```powershell
cd backend
Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force database\__pycache__ -ErrorAction SilentlyContinue
python app.py
```

The database tables will be automatically recreated.

---

### Problem: Import errors after code changes

**Solution: Clear Python cache**
```powershell
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\backend"
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force database\__pycache__
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
```

---

## 📁 Project Structure

```
BioMatch/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── biomatch.db         # SQLite database
│   ├── requirements.txt    # Python dependencies
│   ├── test_blood_request.py  # API test suite
│   └── database/           # Database modules
│       ├── __init__.py
│       ├── db_init.py      # Database initialization
│       ├── inventory.py    # Blood inventory operations
│       ├── donation.py     # Donation management
│       ├── hospital.py     # Hospital management
│       ├── user.py         # User authentication
│       ├── transaction.py  # Transaction tracking
│       └── donor.py        # Donor management
│
├── frontend/
│   ├── main.py             # Main application entry
│   ├── login_page.py       # Login UI
│   ├── signup_page.py      # Signup UI
│   └── blood_request_page.py  # Blood request feature UI
│
└── md/                     # Documentation
    └── docu4endpoints.md   # API endpoint documentation
```

---

## 🔑 API Endpoints

### Blood Request Endpoint
- **URL:** `POST http://127.0.0.1:5000/api/v1/blood/request`
- **Content-Type:** `application/json`

**Request Body:**
```json
{
    "blood_type": "A+",
    "quantity_needed": 3,
    "priority_level": "High",
    "required_date": "2025-10-20"
}
```

**Response (Success):**
```json
{
    "success": true,
    "available_units": [
        {
            "hospital_name": "City General Hospital",
            "blood_type": "A+",
            "units_available": 45,
            "city": "Manila"
        }
    ]
}
```

---

## 🛑 Stopping the Software

### Stop Frontend
- Close the application window **OR**
- Press `ESC` key (if enabled) **OR**
- Press `CTRL+C` in the frontend terminal

### Stop Backend
- Press `CTRL+C` in the backend terminal

**Output when stopping:**
```
^C
 * Received SIGINT, shutting down...
```

---

## 📊 System Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | Windows 10/11 |
| Python | 3.10 or higher |
| RAM | 2 GB minimum |
| Disk Space | 100 MB |
| Network | Localhost (127.0.0.1) |
| Ports | 5000 (backend) |

---

## 🎯 Quick Start Commands

**Complete startup in 3 commands:**

```powershell
# Terminal 1 - Backend
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\backend"; python app.py

# Terminal 2 - Frontend  
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\frontend"; python main.py

# Terminal 3 - Tests (optional)
cd "C:\Users\Ken Ira Talingting\Documents\BioMatch\backend"; python test_blood_request.py
```

---

## ✅ Health Check

Verify everything is working:

```powershell
# 1. Check backend is responding
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/hospitals" -Method GET

# 2. Check database exists
Test-Path "C:\Users\Ken Ira Talingting\Documents\BioMatch\backend\biomatch.db"

# 3. Check Python can import modules
cd backend
python -c "from database import initialize_db; print('✅ Imports successful')"
```

---

## 📝 Notes

- **Backend must be running** before starting frontend
- **Port 5000** must be available for backend
- **Database** is automatically initialized on first run
- **Tkinter** is included with Python (no separate installation needed)
- **Development mode:** Backend runs in development mode (not for production)

---

## 🆘 Getting Help

If you encounter issues:
1. Check this guide's **Troubleshooting** section
2. Review terminal output for error messages
3. Verify all prerequisites are installed
4. Clear Python cache and restart
5. Run the test suite to verify functionality

---

**Last Updated:** October 17, 2025  
**Version:** 1.0  
**Branch:** feature/blood-request-ui
