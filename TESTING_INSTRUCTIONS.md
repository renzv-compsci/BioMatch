# Testing Instructions for BioMatch Changes

## What Changed?

We've fixed the fundamental logic separation between SENDING and RECEIVING blood requests:

1. **Request Blood Page** (Sending Point):

   - Shows requests SENT BY your hospital TO other hospitals
   - Filter: `requesting_hospital_id = your_hospital`
   - Table shows: "Sent Requests (From This Hospital)"

2. **Blood Requests Page** (Receiving Point):

   - Shows requests RECEIVED BY your hospital FROM other hospitals
   - Filter: `source_hospital_id = your_hospital`
   - Table shows: "Received Blood Requests (From Other Hospitals)"
   - Has Approve/Reject buttons

3. **Hospital-Specific Data**:
   - Each hospital only sees their own requests
   - Hospital C will NOT see transactions between Hospital A and Hospital B

## How to Test

### Step 1: Restart Backend

```powershell
cd backend
python app.py
```

**Expected**: Server starts on http://127.0.0.1:5000

### Step 2: Restart Frontend

```powershell
# In new terminal, from project root
python frontend/main.py
```

**Expected**: Tkinter window opens

### Step 3: Login as Hospital 1

- Hospital ID: 1
- Password: hospital123

### Step 4: Test Sending a Request

1. Click search bar in header
2. Type "AB+" (or any blood type)
3. Click search button
4. Results window shows hospitals with that blood
5. Double-click on a hospital (e.g., Hospital 2)
6. Fill in the request form:
   - Units: 2
   - Patient Name: John Doe
   - Patient ID: P12345
   - Doctor: Dr. Smith
   - Priority: Urgent
   - Purpose: Emergency surgery
7. Click "Send Request"
8. **Expected**: Success message

### Step 5: Verify Sent Request

1. Go to "Request Blood" page (sidebar)
2. **Expected**: See your request in "Sent Requests" table
3. Status should be "PENDING"
4. Should show the hospital you sent it TO

### Step 6: Login as Hospital 2 (Receiving Hospital)

1. Logout
2. Login with Hospital ID: 2

### Step 7: Verify Received Request

1. Go to "Blood Requests" page (sidebar)
2. **Expected**: See the request FROM Hospital 1
3. "From Hospital" column shows "Hospital 1" (or whatever name)
4. Status is "PENDING"

### Step 8: Approve the Request

1. Click on the request in the table (to select it)
2. Click "✓ Approve Selected" button
3. Confirm the approval
4. **Expected**: Success message
5. Request status changes to "APPROVED"
6. Your inventory decreases by the approved units
7. Hospital 1's inventory increases

### Step 9: Verify Transaction History

1. Go to "Transactions" page (sidebar)
2. **Expected**: See a transaction showing blood sent to Hospital 1
3. Login as Hospital 1
4. Go to "Transactions" page
5. **Expected**: See a transaction showing blood received from Hospital 2

### Step 10: Test Hospital Isolation

1. Login as Hospital 3 (or any other hospital)
2. Go to "Blood Requests" page
3. **Expected**: Should NOT see the Hospital 1 ↔ Hospital 2 request
4. Go to "Transactions" page
5. **Expected**: Should NOT see the Hospital 1 ↔ Hospital 2 transaction

### Step 11: Test Rejection

1. Login as Hospital 2
2. Repeat steps 3-7 to send another request
3. Login as Hospital 2 (receiver)
4. Select the new request
5. Click "✗ Reject Selected"
6. **Expected**: Status changes to "REJECTED"
7. NO inventory changes
8. NO transaction created

## Expected Behavior Summary

| Action                  | Hospital A (Sender)                      | Hospital B (Receiver)                         | Hospital C (Other) |
| ----------------------- | ---------------------------------------- | --------------------------------------------- | ------------------ |
| **Send Request**        | Shows in "Request Blood" → Sent Requests | Shows in "Blood Requests" → Received Requests | Sees nothing       |
| **Approve Request**     | Inventory increases                      | Inventory decreases                           | Sees nothing       |
| **Transaction Created** | Sees "Received from B"                   | Sees "Sent to A"                              | Sees nothing       |

## Troubleshooting

### "No requests found"

- Make sure you logged in as the correct hospital
- Check that the request was sent TO the hospital you're logged in as (for Blood Requests page)
- Check that the request was sent BY the hospital you're logged in as (for Request Blood page)

### "Insufficient blood inventory"

- The source hospital doesn't have enough blood
- Add donations to increase inventory first

### Backend errors

- Check backend terminal for error messages
- Make sure database is initialized: `python backend/database/db_init.py`

### Frontend not connecting

- Make sure backend is running on http://127.0.0.1:5000
- Check firewall settings

## API Endpoints Changed

### New Endpoint

```
GET /blood_requests/<hospital_id>
```

Returns all requests where hospital is sender OR receiver

### New Endpoints

```
PUT /blood_requests/<request_id>/approve
PUT /blood_requests/<request_id>/reject
```

Approve or reject blood requests

## Documentation

See `PROJECT_DOCUMENTATION.md` for:

- Complete algorithm analysis
- Security implementation (bcrypt)
- Database schema
- All API endpoints
- User flow diagrams
