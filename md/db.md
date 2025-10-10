# 🩸 BioMatch Database Design Documentation

## Overview

This document describes the **SQLite database schema** for the **BioMatch Smart Blood Bank & Compatibility Network**.  
It explains **what each table and field represents**, **why it is needed**, and **its importance** in ensuring **privacy**, **traceability**, **medical safety**, and **efficient matching** in a real-world blood bank system.

---

## 🏥 1. Hospital Table

**Purpose:**  
Stores details for each hospital in the network, including location data for proximity-based search.

| Field       | Type     | Why is it needed?                           | Importance                                        |
|-------------|----------|---------------------------------------------|---------------------------------------------------|
| `id`        | INTEGER  | Unique identifier for each hospital.        | Enables referencing in other tables.              |
| `name`      | TEXT     | Name of the hospital.                       | For display and identification.                   |
| `address`   | TEXT     | Hospital’s physical address.                | For logistics and recordkeeping.                  |
| `contact`   | TEXT     | Contact information for staff.              | For communication and coordination.               |
| `latitude`  | REAL     | Geographic latitude coordinate.             | For distance calculations (nearest hospital).      |
| `longitude` | REAL     | Geographic longitude coordinate.            | For distance calculations (nearest hospital).      |

> *Latitude and longitude enable distance-based searches for optimized emergency response.*

---

## 👩‍⚕️ 2. Staff Table (Hospital Users)

**Purpose:**  
Stores login credentials and links users to their respective hospitals.

| Field           | Type     | Why is it needed?                          | Importance                                    |
|-----------------|----------|--------------------------------------------|-----------------------------------------------|
| `id`            | INTEGER  | Unique user identifier.                    | Enables unique login and user management.      |
| `username`      | TEXT     | Staff login name (unique).                 | Prevents duplicate logins.                    |
| `password_hash` | TEXT     | Securely stores the hashed password.       | Ensures login security and password privacy.   |
| `hospital_id`   | INTEGER  | Links staff to their hospital.             | Restricts user actions to their hospital.      |

> *Only hashed passwords are stored for secure authentication.*

---

## 🩸 3. Donor Table (Anonymous)

**Purpose:**  
Stores **anonymous donor data** to protect privacy while enabling efficient matching and eligibility tracking.

| Field               | Type     | Why is it needed?                         | Importance                                       |
|---------------------|----------|-------------------------------------------|--------------------------------------------------|
| `id`                | INTEGER  | Internal unique identifier for DB.        | Efficient referencing and indexing.              |
| `donor_id_hash`     | TEXT     | Hashed donor ID for privacy.              | Protects donor identity; ensures compliance.     |
| `blood_type`        | TEXT     | Donor’s blood group (A, B, AB, O).        | Core for matching donations and requests.        |
| `rh_type`           | TEXT     | Donor’s Rh factor (+ or -).               | Critical for compatibility.                      |
| `hospital_id`       | INTEGER  | Hospital where donor is registered.       | For hospital-centric donor management.           |
| `last_donation_date`| TEXT     | Date of last donation.                    | For donor safety and legal compliance.           |

> *Real-world blood banks use anonymized donor data to protect privacy while maintaining traceability.*

---

## 🧫 4. Inventory Table

**Purpose:**  
Tracks each hospital’s blood and plasma stock with all medically relevant details.

| Field         | Type     | Why is it needed?                                   | Importance                                   |
|---------------|----------|-----------------------------------------------------|----------------------------------------------|
| `id`          | INTEGER  | Unique record identifier.                           | For referencing and updates.                 |
| `hospital_id` | INTEGER  | Which hospital the stock belongs to.                | Enables hospital-centric stock management.   |
| `blood_type`  | TEXT     | Blood group (A, B, AB, O).                         | Core for matching.                           |
| `rh_type`     | TEXT     | Rh factor (+ or -).                                | For safe transfusions.                       |
| `plasma_type` | TEXT     | Type of blood product (e.g., FFP, Platelets, Cryo).| Tracks blood derivatives.                    |
| `type_of_test`| TEXT     | Quality/screening test performed (e.g., NAT, ELISA)| Ensures safety and compliance.               |
| `quantity`    | INTEGER  | Number of available units/bags.                    | Real-time inventory management.              |
| `last_updated`| TEXT     | Timestamp for the latest update.                    | For data freshness and audits.               |

> *Including plasma and test type ensures traceability and safety in medical use.*

---

## 🔁 5. Transaction Table

**Purpose:**  
Logs every blood movement—donations, transfers, and inter-hospital requests—for full traceability.

| Field                | Type     | Why is it needed?                  | Importance                                        |
|----------------------|----------|------------------------------------|---------------------------------------------------|
| `id`                 | INTEGER  | Unique transaction identifier.     | For audit and referencing.                        |
| `transaction_id_hash`| TEXT     | Hashed transaction ID.             | Ensures data integrity and privacy.               |
| `type`               | TEXT     | "Donation" or "Request".           | Distinguishes transaction types.                  |
| `from_hospital_id`   | INTEGER  | Sending hospital (nullable).       | Enables traceability.                             |
| `to_hospital_id`     | INTEGER  | Receiving hospital.                | Enables traceability.                             |
| `donor_id`           | INTEGER  | Donor involved (nullable).         | Connects donation to donor record.                |
| `blood_type`         | TEXT     | Blood group involved.              | For compatibility tracking.                       |
| `rh_type`            | TEXT     | Rh factor involved.                | For compatibility tracking.                       |
| `plasma_type`        | TEXT     | Type of blood product.             | Complete recordkeeping.                           |
| `type_of_test`       | TEXT     | Screening test type.               | For safety verification.                          |
| `quantity`           | INTEGER  | Number of units moved.             | For accurate inventory tracking.                  |
| `date`               | TEXT     | Transaction date.                  | For logs and audits.                              |
| `status`             | TEXT     | Status (e.g., "pending", "done").  | For process tracking.                             |

> *Transactions provide full audit trails and regulatory compliance.*

---

## 🧱 Final Database Schema (SQLite)

```sql
-- Hospital table
CREATE TABLE Hospital (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    contact TEXT,
    latitude REAL,
    longitude REAL
);

-- Staff table
CREATE TABLE Staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    hospital_id INTEGER NOT NULL,
    FOREIGN KEY (hospital_id) REFERENCES Hospital(id)
);

-- Donor table (anonymous)
CREATE TABLE Donor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id_hash TEXT NOT NULL UNIQUE,
    blood_type TEXT NOT NULL,
    rh_type TEXT NOT NULL,
    hospital_id INTEGER NOT NULL,
    last_donation_date TEXT,
    FOREIGN KEY (hospital_id) REFERENCES Hospital(id)
);

-- Inventory table
CREATE TABLE Inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER NOT NULL,
    blood_type TEXT NOT NULL,
    rh_type TEXT NOT NULL,
    plasma_type TEXT NOT NULL,
    type_of_test TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    last_updated TEXT,
    FOREIGN KEY (hospital_id) REFERENCES Hospital(id)
);

-- Transaction table
CREATE TABLE Transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id_hash TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL, -- 'Donation' or 'Request'
    from_hospital_id INTEGER,
    to_hospital_id INTEGER,
    donor_id INTEGER,
    blood_type TEXT NOT NULL,
    rh_type TEXT NOT NULL,
    plasma_type TEXT NOT NULL,
    type_of_test TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT,
    FOREIGN KEY (from_hospital_id) REFERENCES Hospital(id),
    FOREIGN KEY (to_hospital_id) REFERENCES Hospital(id),
    FOREIGN KEY (donor_id) REFERENCES Donor(id)
);
```