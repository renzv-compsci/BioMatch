# Blood Request UI - Summary

## What Was Built

A Tkinter-based user interface for the Blood Request feature that allows hospitals to search for available blood units across all hospitals.

**UI Components:**
- Form with 4 input fields (blood type dropdown, quantity spinner, priority dropdown, date picker)
- "Search Available Blood" button with loading state
- Results table displaying matching blood units (blood type, hospital name, units available)
- Form validation and error handling
- Clear/reset functionality

**How It Works:**
User fills out the blood request form → Clicks "Search Available Blood" → UI calls `POST /api/v1/blood/request` backend endpoint → Displays results in a sortable table or shows "no results" message.

**Files:**
- `frontend/blood_request_page.py` - Main UI component
- `frontend/main.py` - Updated to integrate the new page

**Access:** Dashboard → "Request Blood" button
