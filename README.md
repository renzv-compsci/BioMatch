  # 🧠 BioMatch: Hospital Blood Bank & Donor Matching System

BioMatch is a Python-based hospital blood bank management and donor-matching system that uses hashing and search algorithms to quickly and securely find compatible blood units across different hospitals.

Each hospital can maintain its own blood inventory, donor database, and transaction history. When a hospital runs low on a certain blood type, it can search for compatible blood available in other hospitals. The system also uses hashing to ensure donor and hospital data security, and optionally, a shortest route algorithm can suggest the nearest hospital with the needed blood supply. This makes blood management efficient, traceable, and life-saving in emergency situations.

---

## 🧩 MVP (Minimum Viable Product)

### 👩‍⚕️ 1. Hospital Login System
Each hospital or authorized staff logs in with:
- **Username / Password** (hashed via SHA-256 or bcrypt)
- Basic authentication and session handling

---

### 🏥 2. Blood Inventory Management
Each hospital maintains its own local blood inventory:
- **Blood Type**
- **Quantity** (bags available)
- **Last Updated Date**
- Staff can add, update, or remove blood units after donation or usage.

---

### 💉 3. Donor Registry
Each donor record contains:
- **Donor ID** (hashed)
- **Name**
- **Blood Type**
- **Hospital Name**
- **Last Donation Date**
- Stored in a hash table or dictionary for O(1) lookups.

---

### 📜 4. Transaction & Donation History
Every donation or request is logged with:
- **Transaction ID** (hashed)
- **Donor/Hospital Info**
- **Type** (Donation / Request)
- **Date, Quantity, Blood Type**

**Example Table:**

| ID      | Type     | Hospital    | Blood Type | Units | Date       |
|---------|----------|-------------|------------|-------|------------|
| TXN-01  | Donation | St. Luke’s  | O+         | 3     | 2025-10-08 |
| TXN-02  | Request  | Manila Med  | A−         | 1     | 2025-10-09 |

---

### 🔍 5. Blood Request & Search Feature (Search Algorithm)
When a hospital requests a blood type, the system uses a search algorithm (Linear or Binary Search, depending on data structure) to look for:
- Compatible blood types (based on compatibility rules)
- Hospitals with available stock

**If found:**
- System displays results (hospital name, quantity, location).

**If not found:**
- Optionally, run a Shortest Route Algorithm (Dijkstra’s) to find the nearest compatible hospital.

#### 🧠 Example:
- *Manila Med requests A− blood.*
- Search algorithm finds A− units in nearby hospital inventories.
- Matches are sorted by availability or proximity.

---

### 🔗 6. Inter-Hospital Request System
- Hospitals can send a request to another hospital if the needed blood is available there.
- Once accepted, both hospitals’ records are updated:
  - Inventory automatically decreases at sender.
  - Transaction added to history for both.

---

## 🧰 Tech Stack

| Layer         | Tool / Framework | Description                                 |
|---------------|------------------|---------------------------------------------|
| Frontend      | Tkinter or Flask | Simple hospital UI (dashboard + forms).     |
| Backend       | Python           | Handles logic for hashing, searching, matching. |
| Database      | SQLite           | Stores hospitals, donors, inventory, and transactions. |
| Search Alg.   | Linear / Binary Search | Finds compatible blood records.      |
| Graph Alg.    | Dijkstra / A* (Optional) | Finds nearest hospital.            |
| Hashing       | SHA-256 / bcrypt | Secure login & hashed record IDs.           |

---

## ⚙️ System Flow

1. **Hospital logs in** (hashed authentication).
2. **Staff checks or updates inventory.**
3. When low on supply → **requests blood type.**
4. System runs:
    - Search algorithm to find compatible blood.
    - (Optional) Shortest route for nearest match.
5. If found → **hospital sends request → transaction is logged.**

---

## 🎯 Core DSA Concepts Used

| Concept             | Where Used                                         |
|---------------------|---------------------------------------------------|
| Hashing             | Login passwords, donor IDs, transaction IDs        |
| Search Algorithm    | Find blood types and compatible hospitals          |
| Graph / Dijkstra    | (Optional) Find the nearest hospitals geographically|
| Data Structures     | Hash tables, arrays/lists for efficient storage and search |

---

## 🚀 Future Enhancements

- Add Google Maps API for real routing.
- Email/SMS notifications when a request is received.
- Dashboard analytics (total blood used, donors, shortages).
- Cloud sync for inter-hospital data sharing.

---

## 💡 Example Use Case

A nurse from City General Hospital needs 2 bags of O− blood.  
She logs in → clicks **Request Blood** → system searches other hospital inventories.

*The algorithm finds 2 matches:*
- **St. Luke’s Hospital** – 5 bags (2 km away)
- **UST Hospital** – 3 bags (5 km away)

She sends a request to St. Luke’s, which accepts → both hospitals’ inventories & logs are updated automatically.

---
