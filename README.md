# 🛒 Smart Inventory & Billing Management System

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-Tkinter-informational.svg)](https://docs.python.org/3/library/tkinter.html)
[![Database](https://img.shields.io/badge/database-SQLite3-brightgreen.svg)](https://www.sqlite.org/)
[![Security](https://img.shields.io/badge/auth-bcrypt-red.svg)](https://github.com/pyca/bcrypt)
[![PDF Engine](https://img.shields.io/badge/reports-ReportLab-orange.svg)](https://www.reportlab.com/)
[![Tests](https://img.shields.io/badge/tests-127%20passed-success.svg)](file:///tests/)

An offline-first, retail-grade **Point of Sale (POS)** and **Smart Inventory Management** desktop application built with **Python**, **Tkinter**, and **SQLite**. Engineered as a comprehensive 30-day internship project, the system combines real-time stock tracking, atomic transactional billing, retail-standard PDF invoice generation, role-based access control, and visual trend analytics.

---

## 📌 Project Overview

**Smart Mart** is designed specifically for single-store retail environments, mini-marts, and consumer outlets. It replaces paper ledgers and fragmented spreadsheets with a unified desktop portal that runs completely offline with zero recurring cloud subscription costs. 

### Core Architecture Highlights
* **Layered Clean Architecture**: Strict separation between Presentation (`ui/`), Business Logic (`services/`), Domain Models (`models/`), and Persistence (`db.py`).
* **Relational Data Integrity**: Backed by SQLite with `PRAGMA foreign_keys = ON`, guaranteeing consistent sales records and cascaded relationships.
* **Safe Soft Deactivation**: Products referenced in historical sales are automatically soft-deactivated when removed, preserving past invoice data and financial accuracy.
* **Responsive Screen Sizing**: Bounded dynamic window geometry (`main.py`) optimized for standard 1366×768 laptops up to 4K desktop monitors.

---

## 🖼️ Application Interface Gallery

### 1. Authentication Screen
![01 Login Screen](docs/01_login.png)
* *Secure entry screen with salted `bcrypt` password verification, role selection, and automatic session initialization.*

### 2. Point of Sale & Checkout Billing
![02 Billing Screen](docs/02_billing.png)
* *Dual-pane POS interface: searchable catalogue with live keystroke filtering on the left, interactive cart with dynamic GST calculation on the right.*

### 3. Product & Stock Management
![03 Products Screen](docs/03_products.png)
* *Inventory ledger with color-coded stock status (`✔ OK` vs `⚠ LOW`), low-stock alert thresholds, and admin-only CRUD forms.*

### 4. Sales Reporting & Trend Analytics
![04 Reports Screen](docs/04_reports.png)
* *Periodic aggregation (Day / Week / Month), embedded dark-palette Matplotlib trend chart with bar value labels, top-selling items ranking, and CSV export.*

### 5. User Administration & RBAC
![05 Users Screen](docs/05_users.png)
* *Administrative user management portal featuring salted bcrypt credential creation, role assignment, and self-deletion safeguards.*

### 6. Relational Database Architecture (ER Diagram)
![06 ER Diagram](docs/06_er_diagram.jpg)
* *Four normalized tables: `users`, `products`, `sales`, and `sale_items` with foreign-key referential integrity.*

---

## 🚀 Key Features

### 🔐 Role-Based Access Control (RBAC)
- **Role Differentiation**: Tailored experience for **Admin** and **Staff** accounts.
- **Sidebar Visibility**: Staff users see an operational subset (`Billing`, `Stock`, `Bill History`); `Reports` and `Users` tabs are restricted to Administrators.
- **Visual Role Badges**: User cards in the sidebar display distinct color-coded badges (`🛡️ ADMIN` in deep indigo vs `👤 STAFF` in deep emerald).
- **Stock Read-Only Mode**: Staff view the catalogue under a read-only *"Stock"* tab with mutating operations guarded against tampering.

### 🧾 Fast Point of Sale Billing
- **Real-Time Keystroke Search**: Instant product filtering across both product names and categories.
- **Cart Management**: Add items, adjust quantities, merge duplicate line items, and clear carts with single-click shortcuts.
- **Atomic Checkout**: Transactional stock deductions ensure sales are either completely committed or rolled back if inventory is insufficient.
- **Customer Tagging**: Seamlessly supports both tagged customer names and anonymous walk-in shoppers.

### 📄 Professional PDF Tax Invoices
- **ReportLab Engine**: Automatically compiles printable A4 tax invoices saved to `invoices/INV-xxxxx.pdf`.
- **Branding Header**: Vector logo badge with shop initials (or custom image fallback), contact details, and `PAID` status indicator.
- **Structured Formatting**: Styled column headers, alternating row colors, divider lines (`HRFlowable`), bold totals row, and store return policy footer.
- **Default OS Viewer**: One-click and double-click opening using Windows default PDF software.

### ⚠️ Real-Time Low-Stock Monitoring
- **Custom Alert Thresholds**: Every product can have an individual alert threshold (defaults to 5 units).
- **Persistent Warning Banner**: Dynamic alert banner appears across dashboard pages when inventory dips below minimum thresholds.
- **Startup Notification**: Alerts managers immediately upon application launch if items require restocking.

### 📊 Business Analytics & Reporting
- **Multi-Period Aggregation**: Summarize gross sales, transaction counts, and items sold across **Day**, **Week**, or **Month** ranges.
- **Embedded Visual Charts**: Integrated Matplotlib bar chart styled to match the dark navy theme, with currency value labels above bars.
- **Data Portability**: One-click CSV export saved to `exports/` for external accounting in Excel or Google Sheets.

---

## 🛠️ Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | 3.9+ | Core application runtime & standard library |
| **GUI Framework** | Tkinter & `ttk` | 8.6 | Native desktop GUI rendering with custom dark palette |
| **Database** | SQLite 3 | 3.x | Zero-config embedded relational database |
| **Authentication** | `bcrypt` | ^4.0 | Salted password hashing and authentication security |
| **Document Generation** | `reportlab` | ^3.6 | Vector-rendered printable A4 PDF tax invoices |
| **Data Visualization** | `matplotlib` | ^3.5 | Trend analytics bar chart embedded in Tkinter canvas |
| **Test Framework** | Python `unittest` | Built-in | Automated testing (127 passing test cases) |

---

## 📁 Repository Directory Structure

```text
smart-inventory-billing/
├── config.py                 # Central store settings, tax percentage, low-stock threshold, paths
├── db.py                     # SQLite schema initialization (users, products, sales, sale_items)
├── utils.py                  # Shared helpers (currency formatting, cross-platform file opener)
├── seed_demo.py              # Catalog seeder with 110+ products across 10 retail categories
├── main.py                   # Application entry point with responsive window sizing
├── requirements.txt          # Python library dependencies
├── README.md                 # Complete system documentation
│
├── docs/                     # Architectural Documentation & Screenshots
│   ├── 01_login.png          # Authentication interface screenshot
│   ├── 02_billing.png        # Point of Sale billing interface screenshot
│   ├── 03_products.png       # Inventory management interface screenshot
│   ├── 04_reports.png        # Sales reports & charts interface screenshot
│   ├── 05_users.png          # Staff user management interface screenshot
│   ├── 06_er_diagram.jpg     # Database Entity-Relationship diagram
│   ├── SYSTEM_REQUIREMENTS.md# Detailed functional and non-functional requirements
│   └── sample_invoice.pdf    # Sample generated PDF tax invoice
│
├── models/                   # Domain Data Classes
│   └── __init__.py           # User, Product, and CartItem models
│
├── services/                 # Business Logic Layer
│   ├── __init__.py           # Unified Services aggregator facade
│   ├── auth_service.py       # Salted bcrypt password hashing and session auth
│   ├── inventory_service.py  # Product catalogue CRUD, stock deduction & search
│   ├── billing_service.py    # Atomic checkout, invoice ledger & stock guards
│   ├── report_service.py     # Periodic aggregations, top sellers & CSV exports
│   └── invoice_service.py    # ReportLab PDF invoice generation engine
│
├── ui/                       # Presentation Layer (Tkinter Desktop GUI)
│   ├── theme.py              # Modern dark palette, custom styles, Card & StatCard widgets
│   ├── login_window.py       # Login dialog with brand panel and error handling
│   ├── dashboard.py          # Master dashboard layout, sidebar navigation, and KPI tiles
│   ├── billing_frame.py      # Point of Sale checkout and cart management frame
│   ├── product_frame.py      # Product catalog table and admin CRUD form frame
│   ├── history_frame.py      # Sales ledger and PDF invoice viewer frame
│   ├── report_frame.py       # Reporting frame with embedded Matplotlib trend charts
│   └── users_frame.py        # Admin user management and role assignment frame
│
├── tests/                    # Automated Test Suite (127 Tests)
│   ├── test_models.py        # Model serialization and validation tests
│   ├── test_utils.py         # Utility helper tests
│   ├── test_auth.py          # Authentication service tests
│   ├── test_inventory.py     # Product catalogue logic tests
│   ├── test_billing.py       # Billing and stock reduction tests
│   ├── test_report.py        # Sales reporting aggregation tests
│   ├── test_invoice.py       # ReportLab PDF generation and layout tests
│   ├── test_services.py      # Core service layer integration tests
│   ├── test_theme.py         # Theme system and UI widget tests
│   ├── test_product_frame.py # Product UI frame tests
│   ├── test_history_frame.py # Bill history UI frame tests
│   ├── test_report_chart.py  # Matplotlib report chart styling tests
│   ├── test_rbac.py          # Role-Based Access Control tests
│   ├── test_edge_cases.py    # Empty cart, PDF errors, duplicate name, screen fit tests
│   └── test_integration.py   # Full system end-to-end user flow integration tests
│
├── invoices/                 # Auto-generated PDF customer invoices
└── exports/                  # Auto-generated CSV sales reports
```

---

## 🗺️ 30-Day Internship Roadmap Progress

| Phase | Milestone | Focus Area | Status |
|---|---|---|---|
| **Phase 1: Foundation** | **Days 1–5** | Project setup, SQLite schema, domain models, utilities, and bcrypt auth | ✅ Complete |
| **Phase 2: Business Logic** | **Days 6–10** | Inventory CRUD, atomic billing, reporting aggregations, PDF engine, service facade | ✅ Complete |
| **Phase 3: Frontend UI** | **Days 11–20**| Tkinter theme, login, dashboard, billing POS, catalog CRUD, history, reports, users | ✅ Complete |
| **Phase 4: Enhancements** | **Days 21–26**| Dark theme polish, low-stock banner alerts, search persistence, chart styles, RBAC | ✅ Complete |
| **Phase 5: Delivery** | **Day 27** | Automated unit tests for AuthService, Inventory, Billing, and ReportService | ✅ Complete |
| | **Day 28** | Edge case guards: empty cart, PDF failure fallback, duplicate names, screen fit | ✅ Complete |
| | **Day 29** | Complete project documentation, screenshots gallery, and setup guides | ✅ Complete |
| | **Day 30** | Final walkthrough, code cleanup, and GitHub Release v1.0.0 | ⏳ Next Up |

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
* **Python 3.9 or higher** installed on your system.
* Windows, macOS, or Linux operating system.

### 2. Clone the Repository
```bash
git clone https://github.com/suman778m-sudo/Smart-Inventory-Billing-Management-System.git
cd Smart-Inventory-Billing-Management-System
```

### 3. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Seed Sample Catalogue (Optional)
Populate the database with **110+ realistic retail products** across 10 categories (Stationery, Electronics, Grocery, Beverages, Snacks, Personal Care, Dairy, Household, Bakery, and Fruits):
```bash
python seed_demo.py
```

### 6. Launch the Application
```bash
python main.py
```

---

## 🔑 Default Login Credentials

The application initializes default credentials upon its initial launch:

| Role | Username | Password | Access Privileges |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Full access: Billing POS, Product CRUD, Financial Reports, Bill History, User Administration |
| **Staff Member** | `staff` | `staff123` | Standard access: Billing POS, Stock Catalogue (Read-Only), Bill History |

---

## 🧪 Running Automated Tests

Run the full automated test suite containing **127 unit and integration tests**:

```bash
# Run all tests with unittest
python -m unittest discover -s tests -v

# Or run specific test modules
python -m unittest tests/test_edge_cases.py
python -m unittest tests/test_rbac.py
python -m unittest tests/test_services.py
python -m unittest tests/test_integration.py
```

---

## 📄 License

This project is open-source software licensed under the **[MIT License](LICENSE)**.

---

## 👨‍💻 Author & Acknowledgments

**Suman Mondal**  
*30-Day Internship Project — Smart Inventory & Billing Management System*  
*Developed with Python, Tkinter, SQLite, ReportLab, and Matplotlib.*
