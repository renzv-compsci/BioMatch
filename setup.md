# Setup Guide

## Prerequisites
- Python 3.8 or higher
- pip

## Installation

1. **Clone/Download the repository**
   ```bash
   cd BioMatch
   ```

2. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run the backend server**
   ```bash
   cd backend
   python app.py
   ```
   Backend will run on `http://127.0.0.1:5000`

4. **Run the frontend** (in a new terminal)
   ```bash
   cd frontend
   python main.py
   ```

## Quick Start
1. Register a hospital on the welcome screen
2. Create a user account linked to the hospital
3. Login and start managing blood inventory

## Troubleshooting
- **Port already in use**: Change port in `backend/app.py` (last line)
- **Module not found**: Reinstall requirements with `pip install -r backend/requirements.txt`
- **Database errors**: Delete `biomatch.db` in backend folder and restart
