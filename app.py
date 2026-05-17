"""
============================================
Online Subscription Management System
Main Flask Application (app.py)
============================================
This is the main backend file for the project.
It handles all routes, database operations, and
user authentication.

Tech Stack: Python Flask + SQLite + Bootstrap 5
============================================
"""

# ---------- Import Required Libraries ----------
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta
import qrcode
from io import BytesIO

# ---------- App Configuration ----------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'submanager_secret_key_2026')  # Secret key for session management

# ---------- UPI Configuration ----------
# Replace with your actual UPI ID for production
UPI_ID = 'testuser@pay'  # Format: username@bankname or phone@upi
MERCHANT_NAME = 'Subscription Manager'
MERCHANT_CATEGORY_CODE = '5411'  # For subscription services

# Ensure the database is created before the first request.
_db_initialized = False

@app.before_request
def initialize_database():
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


# ============================================
# DATABASE SETUP
# ============================================

def get_db():
    """
    Connect to the SQLite database.
    Returns a database connection object.
    """
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    conn = sqlite3.connect(db_path)
    return conn


def init_db():
    """
    Initialize the database by creating all required tables.
    This function runs when the app starts for the first time.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    # Migration: Ensure all existing users have is_admin set to 0 instead of NULL
    cursor.execute('UPDATE users SET is_admin = 0 WHERE is_admin IS NULL')

    # Create Plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_name TEXT NOT NULL,
            price REAL NOT NULL,
            duration INTEGER NOT NULL,
            features TEXT NOT NULL
        )
    ''')

    # Create Subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (plan_id) REFERENCES plans(id)
        )
    ''')

    # Create Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            payment_status TEXT DEFAULT 'success',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ---------- Create Default Admin Account ----------
    # Admin email: admin@submanager.com | Password: admin123
    admin_exists = cursor.execute(
        'SELECT id FROM users WHERE email = ?', ('admin@submanager.com',)
    ).fetchone()

    if not admin_exists:
        hashed_pw = generate_password_hash('admin123')
        cursor.execute(
            'INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)',
            ('Admin', 'admin@submanager.com', hashed_pw, 1)
        )

    # ---------- Create Default Plans ----------
    plans_exist = cursor.execute('SELECT COUNT(*) FROM plans').fetchone()[0]

    if plans_exist == 0:
        default_plans = [
            ('Basic Plan', 299, 30,
             '5 Users, 10GB Storage, Email Support, Basic Analytics'),
            ('Standard Plan', 599, 90,
             '25 Users, 50GB Storage, Priority Support, Advanced Analytics, API Access'),
            ('Premium Plan', 999, 365,
             'Unlimited Users, 200GB Storage, 24/7 Support, Full Analytics, API Access, Custom Branding'),
        ]
        cursor.executemany(
            'INSERT INTO plans (plan_name, price, duration, features) VALUES (?, ?, ?, ?)',
            default_plans
        )

    conn.commit()
    conn.close()


# ============================================
# ROUTES - HOME PAGE
# ============================================

@app.route('/')
def home():
    """Display the home page."""
    return render_template('index.html')


# ============================================
# ROUTES - USER AUTHENTICATION
# ============================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    GET: Display the registration form.
    POST: Process the registration data.
    """
    if request.method == 'POST':
        # Get form data
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate inputs
        if not name or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('register'))

        # Check if email already exists
        conn = get_db()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash('Email already registered! Please login.', 'warning')
            return redirect(url_for('login'))

        # Hash password and save user
        hashed_password = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            (name, email, hashed_password)
        )
        conn.commit()
        conn.close()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    GET: Display the login form.
    POST: Verify credentials and create session.
    """
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        # Find user in database
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        conn.close()

        # Verify credentials
        if user and check_password_hash(user[3], password):
            # Set session variables
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            session['is_admin'] = bool(user[4])

            flash(f'Welcome back, {user[1]}!', 'success')

            # Redirect admin to admin dashboard
            if user[4]:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clear the session and log the user out."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ============================================
# ROUTES - SUBSCRIPTION PLANS
# ============================================

@app.route('/plans')
def plans():
    """Display all available subscription plans."""
    conn = get_db()
    all_plans = conn.execute('SELECT * FROM plans').fetchall()
    conn.close()
    return render_template('plans.html', plans=all_plans)


# ============================================
# ROUTES - USER DASHBOARD
# ============================================

@app.route('/dashboard')
def dashboard():
    """
    Display the user dashboard.
    Shows active subscription and payment history.
    """
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db()

    # Get the user's latest active subscription with plan details
    subscription = conn.execute('''
        SELECT s.id, s.user_id, s.plan_id, s.plan_id, s.start_date, s.end_date,
               s.status, p.plan_name, p.price, p.duration
        FROM subscriptions s
        JOIN plans p ON s.plan_id = p.id
        WHERE s.user_id = ?
        ORDER BY s.id DESC LIMIT 1
    ''', (user_id,)).fetchone()

    # Get payment history
    payments = conn.execute(
        'SELECT * FROM payments WHERE user_id = ? ORDER BY id DESC',
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template('dashboard.html',
                           subscription=subscription,
                           payments=payments)


# ============================================
# ROUTES - SUBSCRIBE TO A PLAN
# ============================================

@app.route('/subscribe/<int:plan_id>')
def subscribe(plan_id):
    """
    Redirect user to the payment page for the selected plan.
    """
    if 'user_id' not in session:
        flash('Please login to subscribe.', 'warning')
        return redirect(url_for('login'))

    conn = get_db()
    plan = conn.execute('SELECT * FROM plans WHERE id = ?', (plan_id,)).fetchone()
    conn.close()

    if not plan:
        flash('Plan not found!', 'danger')
        return redirect(url_for('plans'))

    return render_template('payment.html', plan=plan)


@app.route('/process_payment/<int:plan_id>', methods=['POST'])
def process_payment(plan_id):
    """
    Process the mock payment and create subscription.
    In a real app, this would integrate with a payment gateway.
    """
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db()

    # Get plan details
    plan = conn.execute('SELECT * FROM plans WHERE id = ?', (plan_id,)).fetchone()

    if not plan:
        conn.close()
        flash('Plan not found!', 'danger')
        return redirect(url_for('plans'))

    payment_method = request.form.get('payment_method', 'card')
    card_number = request.form.get('card_number', '').replace(' ', '')
    expiry = request.form.get('expiry', '').strip()
    cvv = request.form.get('cvv', '').strip()
    card_name = request.form.get('card_name', '').strip()
    upi_id = request.form.get('upi_id', '').strip()
    upi_confirmed = request.form.get('upi_confirmed')

    def invalid(message):
        conn.close()
        flash(message, 'danger')
        return redirect(url_for('subscribe', plan_id=plan_id))

    try:
        if payment_method == 'card':
            if not card_number.isdigit() or len(card_number) != 16:
                return invalid('Card number must be exactly 16 digits.')

            if not cvv.isdigit() or len(cvv) != 3:
                return invalid('CVV must be exactly 3 digits.')

            try:
                month, year = expiry.split('/')
                month = int(month)
                year = int(year)
                if year < 100:
                    year += 2000
            except ValueError:
                return invalid('Expiry date must be in MM/YY format.')

            if month < 1 or month > 12:
                return invalid('Expiry month must be between 01 and 12.')

            expiry_date = datetime(year, month, 1)
            last_day = (expiry_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            if last_day < datetime.now():
                return invalid('Card expiry date is invalid or has passed.')

            if not card_name:
                return invalid('Cardholder name is required.')

            # Basic validation passed, accept any mock card for demonstration purposes
            pass
        else:
            if not upi_id or '@' not in upi_id:
                return invalid('Please use a valid UPI ID.')
            if upi_confirmed != 'yes':
                return invalid('Please confirm you completed the UPI payment before proceeding.')

        # Calculate subscription dates
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=plan[3])).strftime('%Y-%m-%d')

        # Cancel any existing active subscriptions
        conn.execute(
            "UPDATE subscriptions SET status = 'expired' WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )

        # Create new subscription
        conn.execute(
            'INSERT INTO subscriptions (user_id, plan_id, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)',
            (user_id, plan_id, start_date, end_date, 'active')
        )

        # Record payment
        payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'INSERT INTO payments (user_id, amount, payment_date, payment_status) VALUES (?, ?, ?, ?)',
            (user_id, plan[2], payment_date, 'success')
        )

        conn.commit()
        conn.close()

        # Show payment success page
        return render_template('payment_success.html',
                               plan_name=plan[1],
                               amount=plan[2],
                               date=payment_date)
    except Exception as e:
        import traceback
        return traceback.format_exc(), 500


# ============================================
# ROUTES - CANCEL SUBSCRIPTION
# ============================================

@app.route('/cancel_subscription/<int:sub_id>')
def cancel_subscription(sub_id):
    """Cancel an active subscription."""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db()
    conn.execute(
        "UPDATE subscriptions SET status = 'cancelled' WHERE id = ? AND user_id = ?",
        (sub_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    flash('Subscription cancelled successfully.', 'info')
    return redirect(url_for('dashboard'))


# ============================================
# ROUTES - ADMIN PANEL
# ============================================

@app.route('/admin')
def admin_dashboard():
    """
    Display the admin dashboard.
    Only accessible by admin users.
    """
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied! Admin only.', 'danger')
        return redirect(url_for('home'))

    conn = get_db()

    # Get all data for admin
    all_plans = conn.execute('SELECT * FROM plans').fetchall()
    all_users = conn.execute('''
        SELECT u.id, u.name, u.email, p.plan_name, s.status
        FROM users u
        LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'
        LEFT JOIN plans p ON s.plan_id = p.id
        WHERE u.is_admin = 0 OR u.is_admin IS NULL
    ''').fetchall()

    # Get subscriptions with user and plan names
    all_subs = conn.execute('''
        SELECT s.id, s.user_id, s.plan_id, s.status, s.start_date, s.end_date,
               COALESCE(u.name, 'Deleted User'), COALESCE(p.plan_name, 'Unknown Plan')
        FROM subscriptions s
        LEFT JOIN users u ON s.user_id = u.id
        LEFT JOIN plans p ON s.plan_id = p.id
        ORDER BY s.id DESC
    ''').fetchall()

    # Get payments with user names
    all_payments = conn.execute('''
        SELECT p.id, p.user_id, p.amount, p.payment_date, p.payment_status,
               COALESCE(u.name, 'Deleted User')
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.id DESC
    ''').fetchall()

    conn.close()

    return render_template('admin.html',
                           plans=all_plans,
                           users=all_users,
                           subscriptions=all_subs,
                           payments=all_payments)


@app.route('/admin/add_plan', methods=['POST'])
def add_plan():
    """Add a new subscription plan (admin only)."""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))

    plan_name = request.form['plan_name'].strip()
    price = float(request.form['price'])
    duration = int(request.form['duration'])
    features = request.form['features'].strip()

    conn = get_db()
    conn.execute(
        'INSERT INTO plans (plan_name, price, duration, features) VALUES (?, ?, ?, ?)',
        (plan_name, price, duration, features)
    )
    conn.commit()
    conn.close()

    flash(f'Plan "{plan_name}" added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/edit_plan/<int:plan_id>', methods=['GET', 'POST'])
def edit_plan(plan_id):
    """Edit an existing subscription plan (admin only)."""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))

    conn = get_db()

    if request.method == 'POST':
        plan_name = request.form['plan_name'].strip()
        price = float(request.form['price'])
        duration = int(request.form['duration'])
        features = request.form['features'].strip()

        conn.execute(
            'UPDATE plans SET plan_name=?, price=?, duration=?, features=? WHERE id=?',
            (plan_name, price, duration, features, plan_id)
        )
        conn.commit()
        conn.close()

        flash(f'Plan "{plan_name}" updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    # GET request - show edit form
    plan = conn.execute('SELECT * FROM plans WHERE id = ?', (plan_id,)).fetchone()
    conn.close()

    if not plan:
        flash('Plan not found!', 'danger')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_plan.html', plan=plan)


@app.route('/admin/delete_plan/<int:plan_id>')
def delete_plan(plan_id):
    """Delete a subscription plan (admin only)."""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))

    conn = get_db()
    conn.execute('DELETE FROM plans WHERE id = ?', (plan_id,))
    conn.commit()
    conn.close()

    flash('Plan deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


# ============================================
# ROUTES - ABOUT PAGE
# ============================================

@app.route('/about')
def about():
    """Display the about/contact page."""
    return render_template('about.html')


# ============================================
# ROUTES - QR CODE GENERATION
# ============================================

@app.route('/generate_qr')
def generate_qr():
    """
    Generate a dummy QR code for testing.
    Returns a QR code image that encodes dummy payment information.
    """
    # Create QR code data (dummy subscription payment info)
    qr_data = {
        'payment_id': 'PAY-2026-001',
        'user': 'Test User',
        'amount': 299,
        'status': 'success',
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Format data as string
    qr_text = f"Payment ID: {qr_data['payment_id']}\nUser: {qr_data['user']}\nAmount: {qr_data['amount']}\nStatus: {qr_data['status']}\nDate: {qr_data['date']}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes buffer
    img_io = BytesIO()
    qr_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', as_attachment=False)


@app.route('/generate_subscription_qr/<int:subscription_id>')
def generate_subscription_qr(subscription_id):
    """
    Generate QR code for a specific subscription.
    Encodes subscription details.
    """
    if 'user_id' not in session:
        flash('Please login to access this feature.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db()
    subscription = conn.execute('''
        SELECT s.id, s.start_date, s.end_date, s.status, p.plan_name, p.price
        FROM subscriptions s
        JOIN plans p ON s.plan_id = p.id
        WHERE s.id = ? AND s.user_id = ?
    ''', (subscription_id, session['user_id'])).fetchone()
    
    conn.close()
    
    if not subscription:
        flash('Subscription not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    # Create QR code data
    qr_text = f"Subscription ID: {subscription[0]}\nPlan: {subscription[4]}\nPrice: {subscription[5]}\nStatus: {subscription[3]}\nStart: {subscription[1]}\nEnd: {subscription[2]}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes buffer
    img_io = BytesIO()
    qr_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', as_attachment=False)


@app.route('/test_qr')
def test_qr():
    """Test page displaying the dummy QR code."""
    return render_template('test_qr.html')


# ============================================
# ROUTES - UPI PAYMENT QR CODE
# ============================================

def generate_upi_string(upi_id, name, amount, description):
    """
    Generate UPI payment string in proper format.
    Format: upi://pay?pa=UPI_ID&pn=NAME&am=AMOUNT&tn=DESCRIPTION&tr=REF_ID
    """
    from urllib.parse import quote
    
    # Ensure amount is properly formatted
    amount_str = f"{float(amount):.2f}"
    
    # Build UPI string
    upi_string = f"upi://pay?pa={upi_id}&pn={quote(name)}&am={amount_str}&tn={quote(description)}"
    
    return upi_string


@app.route('/generate_upi_qr/<int:plan_id>')
def generate_upi_qr(plan_id):
    """
    Generate UPI payment QR code for a specific plan.
    QR code contains UPI payment details.
    """
    conn = get_db()
    plan = conn.execute('SELECT * FROM plans WHERE id = ?', (plan_id,)).fetchone()
    conn.close()
    
    if not plan:
        return "Plan not found", 404
    
    # Generate UPI string
    upi_string = generate_upi_string(
        upi_id=UPI_ID,
        name=MERCHANT_NAME,
        amount=plan[2],  # plan price
        description=f"Subscription: {plan[1]}"
    )
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for payment QR
        box_size=10,
        border=2,
    )
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    # Create image with colors
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes buffer
    img_io = BytesIO()
    qr_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', as_attachment=False)


@app.route('/payment_upi/<int:plan_id>')
def payment_upi(plan_id):
    """
    Display UPI payment page with QR code.
    """
    if 'user_id' not in session:
        flash('Please login to subscribe.', 'warning')
        return redirect(url_for('login'))

    conn = get_db()
    plan = conn.execute('SELECT * FROM plans WHERE id = ?', (plan_id,)).fetchone()
    conn.close()

    if not plan:
        flash('Plan not found!', 'danger')
        return redirect(url_for('plans'))

    # Generate UPI string for display
    upi_string = generate_upi_string(
        upi_id=UPI_ID,
        name=MERCHANT_NAME,
        amount=plan[2],
        description=f"Subscription: {plan[1]}"
    )

    return render_template('payment_upi.html', 
                         plan=plan,
                         upi_id=UPI_ID,
                         merchant_name=MERCHANT_NAME,
                         upi_string=upi_string,
                         plan_id=plan_id)


# ============================================
# RUN THE APPLICATION
# ============================================

if __name__ == '__main__':
    # Initialize the database when the app starts
    init_db()
    print('=' * 50)
    print('  Online Subscription Management System')
    print('  Running on: http://127.0.0.1:5000')
    print('  Admin Login: admin@submanager.com / admin123')
    print('=' * 50)
    # Run the Flask development server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
