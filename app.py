from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import database as db
import auth

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'  # Change this!

# Initialize the database
db.create_tables()

# ========== AUTHENTICATION ROUTES ==========

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        # Validate password strength
        is_valid, message = auth.validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('register.html')
        
        # Validate email
        if not auth.validate_email(email):
            flash('Invalid email address!', 'error')
            return render_template('register.html')
        
        # Create user
        success, user_id, message = db.create_user(username, email, password)
        
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        success, user_id, message = db.authenticate_user(username, password)
        
        if success:
            session['user_id'] = user_id
            session['username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash(message, 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ========== MAIN ROUTES ==========

@app.route('/')
def home():
    """Home page - shows user's expenses"""
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to view your expenses.', 'info')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    expenses = db.get_expenses_by_user(user_id)
    total = db.get_total_expenses(user_id)
    categories = db.get_expenses_by_category(user_id)
    today_total = db.get_today_total(user_id)
    
    return render_template('index.html', 
                         expenses=expenses, 
                         total=total,
                         categories=categories,
                         today_total=today_total,
                         username=session.get('username'))

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    """Add a new expense"""
    if 'user_id' not in session:
        flash('Please login to add expenses.', 'info')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        
        db.add_expense(user_id, description, amount, category, date)
        flash('Expense added successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('add.html')

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    """Edit an existing expense"""
    if 'user_id' not in session:
        flash('Please login to edit expenses.', 'info')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    expense = db.get_expense_by_id(expense_id, user_id)
    
    if not expense:
        flash('Expense not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        
        db.update_expense(expense_id, user_id, description, amount, category, date)
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('edit.html', expense=expense)

@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    """Delete an expense"""
    if 'user_id' not in session:
        flash('Please login to delete expenses.', 'info')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db.delete_expense(expense_id, user_id)
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('home'))

# ========== DASHBOARD ROUTE ==========

@app.route('/dashboard')
def dashboard():
    """Dashboard with charts and visualizations"""
    if 'user_id' not in session:
        flash('Please login to view the dashboard.', 'info')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Get data for charts
    months, monthly_totals = db.get_monthly_expenses(user_id)
    categories, category_totals, category_colors = db.get_category_breakdown(user_id)
    days, daily_totals = db.get_daily_spending_last_7_days(user_id)
    top_expenses = db.get_top_expenses(user_id, 5)
    
    # Get overall stats
    total = db.get_total_expenses(user_id)
    today_total = db.get_today_total(user_id)
    categories_count = len(categories)
    
    return render_template('dashboard.html',
                         months=months,
                         monthly_totals=monthly_totals,
                         categories=categories,
                         category_totals=category_totals,
                         category_colors=category_colors,
                         days=days,
                         daily_totals=daily_totals,
                         top_expenses=top_expenses,
                         total=total,
                         today_total=today_total,
                         categories_count=categories_count,
                         username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)