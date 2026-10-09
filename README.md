# Smart Inventory & Billing Management System

A desktop-based **Point of Sale (POS)** and **Inventory Management** application built with **Python** and **Tkinter** as part of an internship project.

---

## 📌 Project Overview

Smart Mart is a full-featured billing and inventory system designed for small retail shops. It allows staff to create bills, track stock, generate PDF invoices, and view sales reports — all from a clean desktop interface.

---

## 🚀 Features

- 🔐 **User Authentication** — Secure login with bcrypt password hashing
- 👥 **Role-Based Access** — Admin and Staff roles with different permissions
- 🧾 **Billing System** — Add products to cart, apply tax, generate bill
- 📄 **PDF Invoice** — Auto-generated professional invoice for every sale
- 📦 **Inventory Management** — Add, edit, delete products; track stock levels
- ⚠️ **Low Stock Alerts** — Visual alerts when products fall below threshold
- 📊 **Sales Reports** — Daily, weekly, monthly reports with bar chart
- 📥 **CSV Export** — Export sales reports to CSV file
- 🕘 **Bill History** — View and reprint any past invoice

---

## 🛠️ Tech Stack

| Layer        | Technology              |
|-------------|--------------------------|
| Language     | Python 3.9+              |
| GUI          | Tkinter (built-in)       |
| Database     | SQLite 3 (built-in)      |
| PDF          | ReportLab                |
| Charts       | Matplotlib               |
| Auth         | bcrypt                   |

---

## 📁 Project Structure

```
smart-inventory-billing/
├── main.py                  # App entry point
├── config.py                # Shop settings, paths, tax rate
├── db.py                    # SQLite connection & schema
├── utils.py                 # Helper functions
├── seed_demo.py             # Sample products loader
├── requirements.txt         # Python dependencies
├── models/
│   └── __init__.py          # Data models (User, Product, CartItem)
├── services/
│   ├── auth_service.py      # Login & user management
│   ├── billing_service.py   # Sale creation & stock update
│   ├── inventory_service.py # Product CRUD
│   ├── invoice_service.py   # PDF invoice generator
│   └── report_service.py    # Sales reports & CSV export
├── ui/
│   ├── theme.py             # Colors, fonts, ttk styles
│   ├── login_window.py      # Login screen
│   ├── dashboard.py         # Main window with sidebar
│   ├── billing_frame.py     # Billing tab
│   ├── product_frame.py     # Products/Stock tab
│   ├── history_frame.py     # Bill history tab
│   ├── report_frame.py      # Reports tab
│   └── users_frame.py       # Users management tab
├── invoices/                # Generated PDF invoices (auto-created)
├── exports/                 # CSV report exports (auto-created)
└── docs/                    # Screenshots
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-inventory-billing.git
cd smart-inventory-billing
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python main.py
```

### 4. (Optional) Load sample products
```bash
python seed_demo.py
```

---

## 🔑 Default Login Credentials

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| Staff | staff    | staff123  |

> ⚠️ Change these passwords after first login for security.

---

## 📸 Screenshots

| Screen | Description |
|--------|-------------|
| Login  | Secure sign-in with brand panel |
| Dashboard | KPI cards, sidebar navigation |
| Billing | Product picker + cart + PDF invoice |
| Products | Inventory table with add/edit/delete |
| Reports | Sales chart + top sellers + CSV |

---

## 👨‍💻 Author

**Suman**  
Internship Project — 2026  

---

## 📄 License

This project is built for educational/internship purposes.
