# Transaction History Feature - Documentation

## Overview

The Transaction History feature provides comprehensive tracking and visualization of all blood-related operations in the BioMatch system. This feature enables hospitals and administrators to monitor donations, requests, and transfers with detailed filtering, statistics, and export capabilities.

---

## Key Features

### 1. **Transaction Tracking**
- Automatic logging of all blood-related operations
- Tracks donations, requests, and transfers
- Records transaction status (pending, completed, cancelled)
- Timestamps for creation and updates

### 2. **Advanced Filtering**
- Filter by transaction type (donation, request, transfer)
- Filter by status (pending, completed, cancelled)
- Adjustable result limit (50, 100, 200 records)
- Real-time filter application

### 3. **Statistics Dashboard**
- Total transaction count
- Breakdown by type (donations, requests, transfers)
- Status distribution (pending, completed, cancelled)
- Units summary (donated, requested)

### 4. **Data Export**
- Export to CSV format
- Timestamped file naming
- Includes all transaction details
- Saved to user's Desktop

### 5. **User Interface Features**
- Sortable columns (click headers to sort)
- Color-coded status indicators:
  - **Green**: Completed transactions
  - **Yellow**: Pending transactions
  - **Red**: Cancelled transactions
- Responsive design with scrollable view
- Comprehensive data display

---

## Database Schema

### Transactions Table

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL,          -- 'donation', 'request', 'transfer'
    blood_type TEXT NOT NULL,                 -- e.g., 'A+', 'O-'
    units INTEGER NOT NULL,                   -- Number of blood units
    hospital_id INTEGER NOT NULL,             -- Hospital initiating transaction
    target_hospital_id INTEGER,               -- Target hospital (for transfers)
    status TEXT DEFAULT 'completed',          -- 'pending', 'completed', 'cancelled'
    priority_level TEXT,                      -- For requests: 'Low', 'Medium', 'High', 'Critical'
    required_date TEXT,                       -- Required date for requests
    notes TEXT,                               -- Additional information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
    FOREIGN KEY (target_hospital_id) REFERENCES hospitals(id)
);
```

---

## API Endpoints

### 1. Get Hospital Transactions

**GET** `/transactions/<hospital_id>`

Retrieve transaction history for a specific hospital with optional filters.

**Query Parameters:**
- `type` (optional): Filter by transaction type ('donation', 'request', 'transfer')
- `status` (optional): Filter by status ('pending', 'completed', 'cancelled')
- `limit` (optional): Maximum records to return (default: 100, max: 500)

**Example Request:**
```
GET /transactions/1?type=donation&status=completed&limit=50
```

**Response:**
```json
{
    "hospital_id": 1,
    "count": 15,
    "transactions": [
        {
            "id": 42,
            "transaction_type": "donation",
            "blood_type": "A+",
            "units": 3,
            "status": "completed",
            "priority_level": null,
            "required_date": null,
            "notes": "Donation from John Doe",
            "created_at": "2025-10-16T10:30:00",
            "updated_at": "2025-10-16T10:30:00",
            "hospital_name": "City General Hospital",
            "target_hospital_name": null
        }
    ]
}
```

### 2. Get All Transactions (Admin)

**GET** `/transactions`

Retrieve all transactions across all hospitals (system-wide view).

**Query Parameters:**
- `type` (optional): Filter by transaction type
- `status` (optional): Filter by status
- `limit` (optional): Maximum records to return

**Example Request:**
```
GET /transactions?status=pending&limit=100
```

### 3. Update Transaction Status

**PUT** `/transactions/<transaction_id>/status`

Update the status of a specific transaction.

**Request Body:**
```json
{
    "status": "completed",
    "notes": "Blood transferred successfully"
}
```

**Response:**
```json
{
    "message": "Transaction status updated successfully",
    "transaction_id": 42,
    "new_status": "completed"
}
```

### 4. Get Transaction Statistics

**GET** `/transactions/statistics/<hospital_id>`

Retrieve statistical summary for a hospital's transactions.

**Response:**
```json
{
    "hospital_id": 1,
    "statistics": {
        "total_transactions": 150,
        "total_donations": 89,
        "total_requests": 45,
        "total_transfers": 16,
        "pending_transactions": 5,
        "completed_transactions": 140,
        "cancelled_transactions": 5,
        "total_donated_units": 267,
        "total_requested_units": 135
    }
}
```

**GET** `/transactions/statistics`

Retrieve system-wide statistics (omit hospital_id).

---

## Frontend Implementation

### Transaction History Page

**Location:** Accessible from Dashboard → "Transaction History" button

**Features:**

1. **Filter Controls**
   - Transaction Type dropdown (All, donation, request, transfer)
   - Status dropdown (All, pending, completed, cancelled)
   - Limit selector (50, 100, 200)
   - Apply Filters button

2. **Statistics Panel**
   - Real-time statistics display
   - Color-coded stat cards
   - Comprehensive metrics

3. **Data Grid**
   - Sortable columns
   - Color-coded rows by status
   - Horizontal and vertical scrolling
   - Responsive layout

4. **Action Buttons**
   - Refresh: Reload current data
   - Export to CSV: Save transactions to file
   - Back to Dashboard: Return to main menu

### Display Columns

| Column | Description | Width |
|--------|-------------|-------|
| ID | Transaction ID | 60px |
| Type | Transaction type | 100px |
| Blood Type | Blood group | 90px |
| Units | Number of units | 70px |
| Hospital | Initiating hospital | 150px |
| Target Hospital | Recipient hospital | 150px |
| Status | Current status | 90px |
| Priority | Priority level | 80px |
| Date | Creation timestamp | 150px |
| Notes | Additional info | 200px |

---

## Best Practices Implemented

### 1. **Data Integrity**
- Foreign key constraints ensure referential integrity
- Automatic timestamp management
- Transaction validation before insertion

### 2. **Performance Optimization**
- Indexed queries on hospital_id and transaction_type
- Result limiting to prevent memory issues
- Efficient JOIN operations

### 3. **Security**
- Input validation on all endpoints
- SQL injection prevention through parameterized queries
- Type checking and sanitization

### 4. **User Experience**
- Color-coded visual feedback
- Intuitive filtering
- Responsive design
- Export functionality for reporting

### 5. **Maintainability**
- Well-documented code
- Modular function design
- Consistent naming conventions
- Comprehensive error handling

---

## Integration with Existing Features

### 1. **Donations**
When a blood donation is added via the `/add_donation` endpoint:
- A donation record is created
- Inventory is updated
- **A transaction record is automatically logged**

### 2. **Blood Requests**
When a blood request is made via `/request_blood`:
- Matching hospitals are searched
- **A transaction record is created with 'request' type**
- Status reflects whether matches were found

### 3. **Future: Transfers**
Planned integration for blood transfers between hospitals:
- Transfer initiation creates transaction
- Both source and target hospitals logged
- Status tracking through transfer lifecycle

---

## Usage Examples

### Example 1: View All Donations for Hospital

**Frontend:**
1. Navigate to Transaction History
2. Select "donation" from Type filter
3. Click "Apply Filters"

**Backend:**
```
GET /transactions/1?type=donation
```

### Example 2: Export Pending Requests

**Frontend:**
1. Select "request" from Type filter
2. Select "pending" from Status filter
3. Click "Apply Filters"
4. Click "Export to CSV"

**Result:** CSV file saved to Desktop with all pending requests

### Example 3: View Transaction Statistics

**Frontend:**
- Statistics automatically load when page opens
- Displayed in the statistics panel

**Backend:**
```
GET /transactions/statistics/1
```

---

## Error Handling

### API Errors

| Error Code | Scenario | Response |
|------------|----------|----------|
| 400 | Invalid filter parameters | Validation error message |
| 404 | Transaction not found | "Transaction not found" |
| 500 | Database error | Generic error message |

### Frontend Errors

- **Connection Error:** Displayed when API is unreachable
- **No Data:** Informational message when no transactions match filters
- **Export Error:** Error dialog if CSV export fails

---

## Future Enhancements

### Planned Features

1. **Date Range Filtering**
   - Add date picker for custom date ranges
   - Filter by created_at or updated_at

2. **Transaction Details Modal**
   - Click row to view full transaction details
   - Show complete notes and metadata

3. **Status Update from UI**
   - Allow status changes directly from UI
   - Confirmation dialog for status updates

4. **Advanced Analytics**
   - Charts and graphs for transaction trends
   - Blood type distribution analysis
   - Time-series visualization

5. **Notification System**
   - Real-time alerts for pending transactions
   - Email notifications for critical requests

6. **Transfer Workflow**
   - Complete implementation of transfer tracking
   - Approval workflow for transfers
   - Multi-step status tracking

---

## Testing

### Manual Testing Checklist

- [ ] Create donation and verify transaction logged
- [ ] Make blood request and verify transaction created
- [ ] Apply each filter type independently
- [ ] Apply multiple filters together
- [ ] Test sorting on each column
- [ ] Export data to CSV
- [ ] Verify statistics calculations
- [ ] Test with empty results
- [ ] Test with large datasets (100+ records)
- [ ] Verify color coding for each status

### API Testing

Use the provided test file: `test_transactions.py`

```bash
cd backend
python test_transactions.py
```

---

## Conclusion

The Transaction History feature provides a robust, user-friendly solution for tracking all blood-related operations in the BioMatch system. With comprehensive filtering, statistics, and export capabilities, it serves as a critical tool for hospital staff to monitor and analyze blood management activities.

The implementation follows best practices in database design, API development, and user interface design, ensuring maintainability, security, and optimal performance.
