# 📦 Online Subscription Management System

A simple and beginner-friendly **full-stack web application** built as a college micro project.

## 🛠️ Tech Stack

| Layer     | Technology        |
|-----------|-------------------|
| Frontend  | HTML, CSS, JavaScript, Bootstrap 5 |
| Backend   | Python Flask      |
| Database  | SQLite            |

## ✨ Features

- **User Authentication** – Register, Login, Logout, Session Management
- **Subscription Plans** – Browse and subscribe to available plans
- **User Dashboard** – View active subscription, payment history, renew/cancel
- **Admin Panel** – Add/Edit/Delete plans, view users, subscriptions & payments
- **Mock Payment** – Simulated payment page with success confirmation
- **About/Contact Page** – Project information and contact form

## 📁 Project Structure

```
/online subscription management system
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database (auto-created)
├── README.md               # This file
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom CSS styles
│   └── js/
│       └── main.js         # Custom JavaScript
│
└── templates/
    ├── base.html            # Base template (navbar + footer)
    ├── index.html           # Home page
    ├── login.html           # Login page
    ├── register.html        # Registration page
    ├── plans.html           # Subscription plans page
    ├── dashboard.html       # User dashboard
    ├── admin.html           # Admin dashboard
    ├── payment.html         # Payment page
    ├── payment_success.html # Payment success page
    ├── edit_plan.html       # Edit plan page (admin)
    └── about.html           # About/Contact page
```

## 🚀 How to Run

### Prerequisites
- Python 3.x installed on your system
- pip (Python package manager)

### Steps

1. **Open terminal** in the project folder

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   ```
   http://127.0.0.1:5000
   ```

## 🔑 Default Accounts

| Role  | Email                    | Password  |
|-------|--------------------------|-----------|
| Admin | admin@submanager.com     | admin123  |

> Register a new account for user access.

## 📊 Database Tables

| Table          | Fields                                         |
|----------------|------------------------------------------------|
| **users**      | id, name, email, password, is_admin            |
| **plans**      | id, plan_name, price, duration, features       |
| **subscriptions** | id, user_id, plan_id, start_date, end_date, status |
| **payments**   | id, user_id, amount, payment_date, payment_status  |

## 📄 Pages

1. Home Page – Hero section and features overview
2. Login Page – User authentication
3. Register Page – New user registration
4. Plans Page – Browse subscription plans
5. User Dashboard – Subscription status and payment history
6. Admin Dashboard – Manage plans, users, and subscriptions
7. Payment Page – Mock payment processing
8. About Page – Project info and contact form

## 👨‍💻 Built For

College Micro Project – Simple, understandable, and demo-ready.

---

*© 2026 SubManager – Online Subscription Management System*
