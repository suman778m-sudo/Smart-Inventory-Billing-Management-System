# Release Notes — Smart Inventory & Billing Management System

**Release Version:** `v1.0.0`  
**Release Date:** November 6, 2026  
**Author:** Suman Mondal  
**Project:** 30-Day Internship Project — Desktop Point of Sale (POS) & Smart Inventory Management System  
**License:** MIT License  

---

## 🌟 Executive Summary

We are proud to present **Version 1.0.0** of the **Smart Inventory & Billing Management System (Smart Mart)**. Built entirely with Python, Tkinter, and SQLite, this milestone marks the complete delivery of all requirements specified in the 30-day internship plan.

The system is an offline-first desktop application designed for single-store retail environments and mini-marts. It delivers fast point-of-sale checkout, automated printable A4 PDF invoices, real-time inventory monitoring with dynamic alert banners, fine-grained Role-Based Access Control (RBAC), and sales trend analytics—all wrapped in a responsive desktop dark palette.

---

## 🚀 Complete Feature Breakdown

### 1. Security & Role-Based Access Control (RBAC)
* **Salted `bcrypt` Password Hashing**: Passwords are never stored in plaintext. All credentials utilize industry-standard salted bcrypt hashes.
* **Role Personas**:
  * **Administrator**: Complete control over billing, inventory catalogue CRUD, financial reports, bill history, and staff user management.
  * **Staff Member**: Operational access limited to Point of Sale billing, read-only stock lookup, and past invoice viewing.
* **Role-Adaptive Sidebar & Badges**: Sidebar filters out `Reports` and `Users` tabs for staff. User card at the bottom displays role badges (`🛡️ ADMIN` in deep indigo `#252458` vs `👤 STAFF` in forest `#0b382d`) with role-colored avatar icons.
* **Safe Self-Deletion Prevention**: Administrators cannot delete their own active accounts, preventing lockout situations.

### 2. Fast Point of Sale (POS) Checkout
* **Live Keystroke Catalogue Search**: Filters items instantly by name or category without page refreshes.
* **Cart Management**: Add items, adjust quantities, aggregate duplicate line items, and clear cart with single-click shortcuts.
* **Atomic Transaction Processing**: Stock is deducted concurrently with sale creation. If any line item has insufficient stock, the entire transaction is rolled back with an informative alert.
* **Dynamic GST Calculation**: Automatically applies configurable sales tax (`config.TAX_PERCENT`) with live subtotal, tax, and grand total updates.
* **Empty Cart Protection**: Aborts accidental checkout attempts when the cart is empty.

### 3. Retail-Grade PDF Invoicing (ReportLab)
* **Automated Invoice Generation**: Invoices are compiled to `invoices/INV-xxxxx.pdf` immediately upon checkout.
* **Branding & Logo Area**: Features a programmatic vector logo badge with store initials (and support for custom image logos via `config.LOGO_PATH`).
* **Visual Dividers & Structured Metadata**: Incorporates `HRFlowable` accent lines, two-column customer/transaction information cards, alternating item row colors, and a bold dark totals row.
* **Policy Footer**: Includes customer thank-you message, 7-day return policy, and computer-generated disclaimer.
* **Default OS Viewer Integration**: Open and print invoices via Windows default PDF reader on demand.
* **Graceful Failure Fallback**: If PDF generation is interrupted (e.g., file permissions or disk limits), the sale remains committed in SQLite and stock is updated, while alerting the cashier with an informative warning dialog.

### 4. Smart Inventory & Low-Stock Tracking
* **Catalogue CRUD**: Create, edit, and deactivate products with custom pricing, categories, and stock counts.
* **Duplicate Name Prevention**: Enforces unique product naming across active catalogue records.
* **Custom Low-Stock Thresholds**: Configure individualized restock alert limits per product (defaults to 5).
* **Real-Time Low-Stock Banner**: Dashboard displays an alert banner across tabs when inventory falls below minimum thresholds.
* **Startup Restock Alert**: Automatically notifies store managers of low-stock items upon launching the application.
* **Safe Soft Deactivation**: Products present in historical sales are deactivated rather than erased, safeguarding invoice and report integrity.

### 5. Sales Reports & Visual Trend Analytics
* **Flexible Aggregations**: Review revenue, bill counts, and quantities sold across **Day**, **Week**, or **Month** ranges.
* **Embedded Matplotlib Trend Chart**: Displays sales trajectories with theme-matching `#0f172a` canvas, `#5b5ef4` bars, gridlines, value labels, and clean empty states.
* **Top-Selling Ranking**: Identifies best-performing items by quantity sold.
* **CSV Data Export**: One-click data export saved to `exports/` for accounting in Microsoft Excel or Google Sheets.

### 6. Modern Desktop User Interface & Screen Fit
* **Dark Navy Aesthetic**: Deep navy sidebar (`#16193a`), slate cards (`#1e293b`), and vivid indigo highlights (`#5b5ef4`).
* **StatCards**: KPI stat tiles with colored icon chips and positive/negative indicators.
* **Responsive Screen Sizing**: Window geometry algorithm (`compute_window_geometry`) ensures optimal fit on 1366×768 laptops up to 4K desktop screens without clipping controls.
* **One-Click Launchers**: Windows batch scripts (`run_app.bat` and `push_to_github.bat`) for easy launching and repository synchronization.

---

## 🧪 Quality Assurance & Test Verification

The application is verified by a test suite of **127 automated unit and integration tests** with **100% pass rate**:

| Test Module | Tests | Description |
|---|---|---|
| `tests/test_models.py` | 5 | Domain model validation, cart calculations, dataclass equality |
| `tests/test_utils.py` | 5 | Currency formatting, cross-platform file opening helpers |
| `tests/test_auth.py` | 6 | Salted bcrypt hashing, authentication, role verification |
| `tests/test_inventory.py` | 8 | Catalogue CRUD, threshold queries, duplicate checks |
| `tests/test_billing.py` | 8 | Atomic checkout, stock deduction, oversell prevention |
| `tests/test_report.py` | 8 | Multi-period reporting, today summary, CSV export |
| `tests/test_invoice.py` | 7 | ReportLab PDF compilation, vector logo, OS viewer execution |
| `tests/test_services_bundle.py` | 4 | Unified Services facade lifecycle |
| `tests/test_theme.py` | 8 | Tkinter styles, font scaling, Card and StatCard widgets |
| `tests/test_product_frame.py` | 7 | Product UI catalogue, selection persistence, CRUD forms |
| `tests/test_history_frame.py` | 5 | Bill history ledger, cashier tracking, double-click PDF open |
| `tests/test_report_chart.py` | 4 | Matplotlib chart styling, bar value labels, empty state |
| `tests/test_rbac.py` | 6 | Admin vs Staff visibility, stock view-only, role badges |
| `tests/test_edge_cases.py` | 7 | Empty cart, PDF failure fallback, duplicate names, screen fit |
| `tests/test_integration.py` | 3 | Full end-to-end Admin, Staff, and Low-Stock user flows |
| `tests/test_services.py` | 19 | Core service suite covering auth, inventory, billing, reports |
| `tests/test_main.py` | 3 | Application window initialization and view routing |
| **TOTAL** | **127** | **Zero Failures, Zero Errors (100% Passing)** |

---

## 📦 Deliverables & File Artifacts

* **Source Code**: Complete Python package (`main.py`, `config.py`, `db.py`, `utils.py`, `models/`, `services/`, `ui/`, `tests/`)
* **Documentation**: `README.md`, `RELEASE_NOTES.md`, `docs/SYSTEM_REQUIREMENTS.md`, `docs/er_diagram.jpg`
* **Demo Data**: `seed_demo.py` with 110+ items across 10 retail categories
* **Launch Scripts**: `run_app.bat`, `push_to_github.bat`
* **License**: MIT License (`LICENSE`)
* **Archive**: `DAY_30_WORK.zip`
