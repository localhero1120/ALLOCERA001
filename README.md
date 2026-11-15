# College Exam Seat Allocation Management System

A full-stack, responsive, and persistent Examination Seat Allocation Management System designed for college administrators, exam coordinators, invigilators, and students. Built with Python Flask, SQLAlchemy (SQLite), Chart.js, Lucide Icons, and ReportLab.

---

## 🚀 Final Run Command

To start the application server, run:

```powershell
python app.py
```

Then open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---


## 📦 Features Implemented

1. **Dashboard & Visual Metrics:**
   - Real-time database metrics: Total students, active departments, exam rooms, capacity, allocated and unallocated students.
   - Interactive Doughnut Chart for department distribution and live allocation progress bars.
   - Quick action shortcuts matching the dashboard reference design.

2. **Department Management:**
   - Dynamic department creation with custom colors and codes (e.g., DS, BCA, CS, Commerce, AI).
   - Validation against duplicate department codes and deletion safeguards.

3. **Student Management & CSV/Excel Import:**
   - Single student manual addition with unique register number constraints.
   - Batch import parser supporting both `.csv` and `.xlsx` formats with validation preview and error logging.
   - Sample CSV download option.

4. **Halls & Seating Management:**
   - Configurable rooms with rows, columns, usable benches, and capacity calculation.
   - **One-Click Multiple Room Creation:** Easily generate 20 or more rooms (e.g., `LH 1` through `LH 20`) in a single click with pre-configured benches.

5. **Visual Seating Plan (Handwritten Diagram Reproduction):**
   - Direct reproduction of the user reference layout:
     - Front **BOARD** banner at the top.
     - **Left Column:** Benches 1, 2, 3, 4, 5.
     - **Middle Column:** Benches 10, 9, 8, 7, 6 (reverse vertical order).
     - **Right Column:** Benches 11, 12, 13, 14, 15.
     - Bench-level **Left** and **Right** seat assignments with department color badges.
   - Interactive modal to view student details, manually assign, or remove students.

6. **Automated Multi-Room Allocation Engine:**
   - **Department Pairing Rules:** Allocate DS on the Left seat and BCA on the Right seat across benches.
   - **Room-to-Room Continuation:** Automatically fills LH 1 first (30 seats); when LH 1 is full, continuation automatically rolls over into LH 2, LH 3, etc.
   - Atomic database transactions with preview simulation mode before committing.

7. **Student "Find My Seat" Portal:**
   - Public search portal for students using their register number and exam selection to find hall, bench number, and side (Left/Right).

8. **Invigilators, Attendance & Reports:**
   - Invigilator staff management.
   - Real-time room attendance marking (Present/Absent).
   - Export reports in CSV, Excel, and printable PDF attendance sheets.

---

## 🧪 Automated Testing

To run the automated test suite:

```powershell
python -m pytest tests/
```
