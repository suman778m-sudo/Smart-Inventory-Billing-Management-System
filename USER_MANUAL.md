# 📖 Smart Inventory & Billing Management System — User Operating Manual

A complete, beginner-friendly operational guide for store managers, cashiers, and administrators on how to run, operate, and maintain the **Smart Inventory & Billing Management System**.

---

## 📑 Table of Contents
1. [System Overview & Login Credentials](#1-system-overview--login-credentials)
2. [How to Launch the Application](#2-how-to-launch-the-application)
3. [Step-by-Step Operating Guide](#3-step-by-step-operating-guide)
   - [A. Creating Customer Bills (Point of Sale POS)](#a-creating-customer-bills-point-of-sale-pos)
   - [B. Managing Products & Inventory Stock](#b-managing-products--inventory-stock)
   - [C. Viewing Past Bills & Reprinting Invoices](#c-viewing-past-bills--reprinting-invoices)
   - [D. Generating Financial Reports & Exporting to Excel/CSV](#d-generating-financial-reports--exporting-to-excelcsv)
   - [E. Managing Users & Staff Accounts](#e-managing-users--staff-accounts)
4. [Roles & Permissions (Admin vs. Staff)](#4-roles--permissions-admin-vs-staff)
5. [Database, Invoices & Export File Storage](#5-database-invoices--export-file-storage)
6. [Troubleshooting & Frequently Asked Questions](#6-troubleshooting--frequently-asked-questions)

---

## 1. System Overview & Login Credentials

When the system opens, you will be prompted to enter your username and password. The system comes pre-configured with two user accounts:

| Role | Username | Password | Purpose & Privileges |
| :--- | :--- | :--- | :--- |
| **🛡️ Administrator** | `admin` | `admin123` | **Full Store Control**: POS Billing, Adding/Editing/Deleting Products, Viewing Financial Reports, Exporting CSVs, and Managing Staff Accounts. |
| **👤 Staff Member** | `staff` | `staff123` | **Front-Desk POS Cashier**: POS Billing, Stock Lookup (Read-Only), and Past Bills viewing. Protected from seeing financial analytics or managing users. |

---

## 2. How to Launch the Application

### Method 1: One-Click Windows Launcher (Recommended)
1. Navigate to the `smart-inventory-billing` folder.
2. Double-click the file named **`run_app.bat`**.
3. The launcher will automatically verify Python, initialize the local database if needed, and open the application window.

### Method 2: From the Command Line / Terminal
1. Open PowerShell or Command Prompt.
2. Navigate to the project directory:
   ```bash
   cd "c:\Users\suman\Downloads\smart-inventory-billing (1)\smart-inventory-billing"
   ```
3. Run:
   ```bash
   python main.py
   ```

*(Optional) If you want to populate the inventory with 110+ sample retail products across 10 categories, run:*
```bash
python seed_demo.py
```

---

## 3. Step-by-Step Operating Guide

---

### A. Creating Customer Bills (Point of Sale POS)
*(This is the primary screen used for retail checkout at the billing counter).*

1. **Log in** as either `admin` or `staff`.
2. Click on the **🛒 Billing** tab in the left sidebar (this is opened by default).
3. **Search for Items:**
   - Type the product name or category into the **Search** box in the top-left corner.
   - The product list filters instantly in real time as you type.
4. **Add Items to the Cart:**
   - Click on the desired item in the product table.
   - Enter the **Quantity** (e.g. `2`).
   - Click **Add to Cart** (or hit Enter).
   - *Note:* If you add the same product again, the cart automatically increases its quantity.
5. **Customer Details (Optional):**
   - Type the customer's name into the **Customer Name** field at the top right.
   - If left empty, it defaults automatically to *"Walk-in Customer"*.
6. **Adjust Cart Quantities or Remove Items:**
   - To remove an item: Select it in the cart and click **Remove Item**.
   - To clear everything and start over: Click **Clear Cart**.
7. **Review the Financial Breakdown:**
   - The summary at the bottom-right calculates **Subtotal**, **GST (18%)**, and **Grand Total** dynamically.
8. **Checkout & Generate Bill:**
   - Click the green **Checkout / Print Bill** button.
   - **What happens immediately:**
     - The stock is atomically deducted from inventory.
     - The system prevents overselling (if an item lacks sufficient stock, checkout safely halts and notifies you).
     - A professional PDF invoice (e.g. `INV-00001.pdf`) is created in the `invoices/` folder and automatically opens on your screen for instant printing or sharing.

---

### B. Managing Products & Inventory Stock
*(Admin has full edit rights under "Products"; Staff has a read-only "Stock" view).*

1. Click on **📦 Products** (or **📦 Stock** for Staff) in the sidebar.
2. **Reviewing Inventory Status:**
   - The table displays: `ID`, `Name`, `Category`, `Price (₹)`, `Stock`, `Min Stock Alert`, and `Status`.
   - The **Status** column shows:
     - `✔ OK` in soft green when stock is healthy.
     - `⚠ LOW` in amber/red when stock is less than or equal to the alert threshold.
3. **Filtering by Category:**
   - Select a category from the dropdown (e.g., Grocery, Electronics, Bakery, Dairy) to narrow down items.
4. **Adding a New Product (Admin Only):**
   - In the right-hand form, enter:
     - **Product Name** (must be unique)
     - **Category**
     - **Unit Price (₹)** (must be greater than 0)
     - **Current Stock Quantity** (0 or more)
     - **Low Stock Alert Threshold** (e.g. `5`)
   - Click **Save Product**.
5. **Updating an Existing Product (Admin Only):**
   - Click any product in the table. Its details will load into the form.
   - Modify the price, stock, or threshold.
   - Click **Update Product**.
6. **Deleting a Product (Admin Only):**
   - Select the product in the table and click **Delete Product**.
   - *Safety Feature:* If the product was ever part of a past sale, the system **soft-deactivates** it instead of hard-deleting, preserving all past financial reports and bill histories intact.

---

### C. Viewing Past Bills & Reprinting Invoices
*(Used when a customer asks for a duplicate receipt or when reviewing the day's sales).*

1. Click on **📜 Bill History** in the sidebar.
2. **Locate a Bill:**
   - Search by **Invoice Number** (e.g. `INV-00003`) or **Customer Name** using the search bar.
3. **View Invoice Details:**
   - Click on any row to view its line-by-line item details, quantity, rate, subtotal, and tax.
4. **Open / Reprint PDF:**
   - Double-click the transaction row (or click the **Open Invoice PDF** button).
   - The original PDF receipt opens in your default PDF software (Adobe Reader, Microsoft Edge, Chrome, etc.) ready to print.

---

### D. Generating Financial Reports & Exporting to Excel/CSV
*(Restricted to Admin accounts).*

1. Click on **📊 Reports** in the sidebar.
2. **Select Report Period:**
   - Choose from the dropdown:
     - **Today** (sales generated during the current date)
     - **Weekly** (daily breakdown for the past 7 days)
     - **Monthly** (sales aggregated over the current month)
3. **Inspect Key Performance Indicator (KPI) Cards:**
   - **Total Gross Revenue:** Total currency earned in the selected period.
   - **Total Bills:** Count of completed sales transactions.
   - **Items Sold:** Cumulative quantity of physical goods sold.
4. **Visual Sales Chart:**
   - An interactive Matplotlib bar chart renders the revenue distribution with bold currency values displayed over each bar.
5. **Top 5 Bestselling Items:**
   - A ranked leaderboard highlights which items sell the most units.
6. **Export Data to Excel / CSV:**
   - Click **Export to CSV**.
   - A timestamped spreadsheet file is generated inside the `exports/` folder (e.g., `exports/sales_report_20261107.csv`), which can be opened in Microsoft Excel or Google Sheets.

---

### E. Managing Users & Staff Accounts
*(Restricted to Admin accounts).*

1. Click on **👥 Users** in the sidebar.
2. **View Existing Users:**
   - The table lists all usernames, roles (`Admin` or `Staff`), and creation dates.
3. **Create a New User:**
   - Enter a unique **Username**.
   - Enter a secure **Password** (must be at least 6 characters long).
   - Select the **Role**:
     - Choose `Staff` for checkout cashiers.
     - Choose `Admin` for assistant store managers.
   - Click **Create User**. Passwords are encrypted using salted `bcrypt` algorithms.
4. **Delete a User Account:**
   - Select the user in the table and click **Delete User**.
   - *Built-in Security Guards:*
     - You **cannot** delete your own currently logged-in account.
     - You **cannot** delete the last remaining Administrator account.

---

## 4. Roles & Permissions (Admin vs. Staff)

| Feature / Action | Admin | Staff |
| :--- | :---: | :---: |
| **Point of Sale (POS) Billing** | ✅ Yes | ✅ Yes |
| **Search Products & View Prices** | ✅ Yes | ✅ Yes |
| **Create Customer Invoices** | ✅ Yes | ✅ Yes |
| **Reprint Past Invoices (Bill History)** | ✅ Yes | ✅ Yes |
| **Add / Edit / Delete Products** | ✅ Yes | ❌ Read-Only |
| **Adjust Stock Quantities** | ✅ Yes | ❌ Read-Only |
| **Access Financial Reports & Analytics** | ✅ Yes | ❌ Hidden |
| **Export Sales Data to CSV** | ✅ Yes | ❌ Hidden |
| **Create / Manage User Accounts** | ✅ Yes | ❌ Hidden |

---

## 5. Database, Invoices & Export File Storage

All application data is kept locally on your computer with zero cloud dependencies:

* **Database File:**
  - `smart-inventory-billing/inventory.db`
  - SQLite relational database file holding all users, catalog items, and sales transactions.
  - *Tip:* To back up your store data, simply make a copy of this `inventory.db` file to a secure flash drive or backup folder.
* **Customer PDF Invoices:**
  - `smart-inventory-billing/invoices/`
  - Invoices are named in the format `INV-XXXXX.pdf` (e.g. `INV-00001.pdf`).
* **Exported CSV Reports:**
  - `smart-inventory-billing/exports/`
  - CSV files suitable for accounting, tax reporting, or opening in Microsoft Excel.

---

## 6. Troubleshooting & Frequently Asked Questions

### Q1: The application does not start when I double-click `run_app.bat`.
* **Fix:** Ensure Python 3.9+ is installed and checked with *"Add Python to PATH"* during installation. You can test this by opening PowerShell and typing `python --version`.

### Q2: An invoice PDF was generated, but it didn't open on screen.
* **Fix:** Windows opens PDFs using whatever program is set as your default PDF viewer (such as Microsoft Edge, Chrome, or Adobe Acrobat). You can always find your invoices manually inside the `smart-inventory-billing/invoices/` folder.

### Q3: A product cannot be deleted.
* **Fix:** If a product was already purchased in a past sale, it cannot be physically erased from the database to avoid breaking historical records. Instead, the system deactivates it so it will no longer appear in the POS billing catalog while leaving old bills valid.

### Q4: How do I run the automated diagnostic test suite?
* **Fix:** Open terminal in the project folder and run:
  ```bash
  python -m unittest discover tests
  ```
  All 127 tests should pass with `OK`.
