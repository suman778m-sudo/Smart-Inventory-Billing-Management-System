# Smart-Inventory-Billing-Management-System
A shop management system that keeps track of your products and stock, creates bills for customers, warns you when items are running low, and shows how much you sold each day, week and month.


Understand what the shop needs and plan how the application will work before starting any work on it.

## What I did

- Read the problem statement carefully and listed the required features.
- Planned the modules and how they connect.
- Set up the development environment (Python and the project folder).
- Ran the starter project once and looked at how it is organised.
- Reviewed the screens and started thinking about a cleaner, more attractive design.

## Required features I identified

| # | Required feature | How it should work |
|---|---|---|
| 1 | Product management | Add, update and delete products, and keep track of stock. |
| 2 | Billing | Pick products, make a cart, calculate tax and total, and create a printable invoice. |
| 3 | Low-stock alert | Warn the user when an item is running low. |
| 4 | Sales reports | Show total sales by day, week and month. |
| 5 | Login with roles | Admin can use everything. Staff can only bill and view stock and history. |

## Plan: how the app will work

1. The user logs in as Admin or Staff.
2. The shop adds its products with price, quantity and a low-stock level.
3. The cashier builds a bill. Tax and total are calculated automatically.
4. When the bill is generated, the stock goes down and a PDF invoice is created.
5. Items that fall to their low level are shown in red with a warning.
6. The Admin opens reports to see sales by day, week or month.

## Project layout I planned

- **Screens:** what the user sees (login, billing, products, history, reports, users).
- **Rules:** the logic behind each feature (login, stock, billing, reports).
- **Data:** where users, products and sales are stored.

Keeping these three parts separate makes the project easier to test and change.

## Outcome

- Clear list of features and how they connect.
- Environment ready to work in.
- A plan for the next day: run the app and test the main features.

- Get the application running on my computer, test the main features, and write down the assumptions.

## What I did

### 1. Installed Python and prepared the project
- Installed Python and made sure it is added to the system PATH.
- Opened PowerShell inside the project folder.
- Created a virtual environment and installed the required packages:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ran the application
```
python main.py
```
Logged in with the default accounts (`admin` and `staff`) and checked that each role sees the correct screens.

### 3. Problems I faced and how I fixed them

| Problem | Cause | Fix |
|---|---|---|
| "Python was not found" | Python was not installed or not on PATH | Installed Python with "Add to PATH" ticked, then opened a new PowerShell window |
| Commands failed when typed together | Two commands were joined on one line | Ran each command on its own line |
| "Cannot find path" for the `ui` folder | PowerShell was in the wrong folder | Opened the folder that contains `main.py` and checked with `dir` |
| App still showed the old design | An older copy of the project was running | Copied the new `ui` folder and `main.py` over the old files |

### 4. Tested the main features

| Feature tested | Result |
|---|---|
| Login with Admin and Staff | Works, and Staff does not see Admin screens |
| Adding and searching products | Works |
| Creating a bill and generating the invoice | Works, and stock goes down after the sale |
| Low-stock alert | Low items show in red, with a banner and pop-up |
| Bill history | Past invoices can be opened again |

### 5. Written work
- Wrote the project **assumptions** (single shop, fixed tax, stock never negative, two roles, and so on).
- Wrote the short description and the README for the GitHub repository.

## Outcome

- The app runs correctly on my computer.
- The main features work as expected.
- Assumptions and repository description are ready.
