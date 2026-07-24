from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import database as db
import auth
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production-2026'  # CHANGE THIS!

# Initialize the database
db.create_tables()

# ========== CUSTOM ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    """Custom 404 page"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 page"""
    return render_template('500.html'), 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Custom 405 page"""
    flash('Method not allowed.', 'error')
    return redirect(url_for('home'))

# ========== AUTHENTICATION ROUTES ==========

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with validation"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate username
        if not username:
            flash('Username is required!', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long!', 'error')
            return render_template('register.html')
        
        if not username.isalnum():
            flash('Username can only contain letters and numbers!', 'error')
            return render_template('register.html')
        
        # Validate email
        if not email:
            flash('Email is required!', 'error')
            return render_template('register.html')
        
        if not auth.validate_email(email):
            flash('Please enter a valid email address!', 'error')
            return render_template('register.html')
        
        # Validate passwords
        if not password:
            flash('Password is required!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        # Validate password strength
        is_valid, message = auth.validate_password(password)
        if not is_valid:
            flash(message, 'error')
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
    """User login with validation"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate input
        if not username:
            flash('Username is required!', 'error')
            return render_template('login.html')
        
        if not password:
            flash('Password is required!', 'error')
            return render_template('login.html')
        
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
    """Home page - shows filtered expenses"""
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to view your expenses.', 'info')
        return redirect(url_for('login'))
    
    try:
        user_id = session['user_id']
        
        # Get search and filter parameters
        search_term = request.args.get('search', '').strip()
        category_filter = request.args.get('category', 'All')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Validate dates
        if date_from:
            try:
                datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format for "Date From"', 'error')
                date_from = ''
        
        if date_to:
            try:
                datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format for "Date To"', 'error')
                date_to = ''
        
        # Get expenses with filters
        expenses = db.search_expenses(user_id, search_term, category_filter, date_from, date_to)
        total = db.get_filtered_total(user_id, search_term, category_filter, date_from, date_to)
        categories = db.get_filtered_categories(user_id, search_term, category_filter, date_from, date_to)
        today_total = db.get_today_total(user_id)
        
        # Get all categories for dropdown
        all_categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Healthcare', 'Education', 'Other']
        
        return render_template('index.html', 
                             expenses=expenses, 
                             total=total,
                             categories=categories,
                             today_total=today_total,
                             username=session.get('username'),
                             search_term=search_term,
                             category_filter=category_filter,
                             all_categories=all_categories,
                             date_from=date_from,
                             date_to=date_to)
    except Exception as e:
        flash(f'An error occurred while loading your expenses. Please try again.', 'error')
        return render_template('index.html', 
                             expenses=[], 
                             total=0,
                             categories=[],
                             today_total=0,
                             username=session.get('username'),
                             search_term='',
                             category_filter='All',
                             all_categories=[],
                             date_from='',
                             date_to='')

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    """Add a new expense with validation"""
    if 'user_id' not in session:
        flash('Please login to add expenses.', 'info')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            user_id = session['user_id']
            description = request.form.get('description', '').strip()
            amount_str = request.form.get('amount', '').strip()
            category = request.form.get('category', '')
            date = request.form.get('date', '')
            
            # Validate description
            if not description:
                flash('Description is required!', 'error')
                return render_template('add.html')
            
            if len(description) < 3:
                flash('Description must be at least 3 characters long!', 'error')
                return render_template('add.html')
            
            # Validate amount
            if not amount_str:
                flash('Amount is required!', 'error')
                return render_template('add.html')
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    flash('Amount must be greater than 0!', 'error')
                    return render_template('add.html')
                if amount > 99999999:
                    flash('Amount is too large! Please enter a reasonable amount.', 'error')
                    return render_template('add.html')
            except ValueError:
                flash('Please enter a valid number for amount!', 'error')
                return render_template('add.html')
            
            # Validate category
            if not category:
                flash('Please select a category!', 'error')
                return render_template('add.html')
            
            all_categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Healthcare', 'Education', 'Other']
            if category not in all_categories:
                flash('Invalid category selected!', 'error')
                return render_template('add.html')
            
            # Validate date
            if not date:
                flash('Please select a date!', 'error')
                return render_template('add.html')
            
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format! Please select a valid date.', 'error')
                return render_template('add.html')
            
            # Add expense
            db.add_expense(user_id, description, amount, category, date)
            flash('Expense added successfully! 💰', 'success')
            return redirect(url_for('home'))
            
        except ValueError as e:
            flash('Please enter a valid amount!', 'error')
            return render_template('add.html')
        except Exception as e:
            flash('An error occurred while adding the expense. Please try again.', 'error')
            return render_template('add.html')
    
    return render_template('add.html')

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    """Edit an existing expense with validation"""
    if 'user_id' not in session:
        flash('Please login to edit expenses.', 'info')
        return redirect(url_for('login'))
    
    try:
        user_id = session['user_id']
        expense = db.get_expense_by_id(expense_id, user_id)
        
        if not expense:
            flash('Expense not found or you do not have permission to edit it.', 'error')
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            description = request.form.get('description', '').strip()
            amount_str = request.form.get('amount', '').strip()
            category = request.form.get('category', '')
            date = request.form.get('date', '')
            
            # Validate description
            if not description:
                flash('Description is required!', 'error')
                return render_template('edit.html', expense=expense)
            
            if len(description) < 3:
                flash('Description must be at least 3 characters long!', 'error')
                return render_template('edit.html', expense=expense)
            
            # Validate amount
            if not amount_str:
                flash('Amount is required!', 'error')
                return render_template('edit.html', expense=expense)
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    flash('Amount must be greater than 0!', 'error')
                    return render_template('edit.html', expense=expense)
                if amount > 99999999:
                    flash('Amount is too large! Please enter a reasonable amount.', 'error')
                    return render_template('edit.html', expense=expense)
            except ValueError:
                flash('Please enter a valid number for amount!', 'error')
                return render_template('edit.html', expense=expense)
            
            # Validate category
            if not category:
                flash('Please select a category!', 'error')
                return render_template('edit.html', expense=expense)
            
            all_categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Healthcare', 'Education', 'Other']
            if category not in all_categories:
                flash('Invalid category selected!', 'error')
                return render_template('edit.html', expense=expense)
            
            # Validate date
            if not date:
                flash('Please select a date!', 'error')
                return render_template('edit.html', expense=expense)
            
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format! Please select a valid date.', 'error')
                return render_template('edit.html', expense=expense)
            
            # Update expense
            db.update_expense(expense_id, user_id, description, amount, category, date)
            flash('Expense updated successfully! ✏️', 'success')
            return redirect(url_for('home'))
        
        return render_template('edit.html', expense=expense)
        
    except Exception as e:
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('home'))

@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    """Delete an expense with confirmation"""
    if 'user_id' not in session:
        flash('Please login to delete expenses.', 'info')
        return redirect(url_for('login'))
    
    try:
        user_id = session['user_id']
        expense = db.get_expense_by_id(expense_id, user_id)
        
        if not expense:
            flash('Expense not found or you do not have permission to delete it.', 'error')
            return redirect(url_for('home'))
        
        db.delete_expense(expense_id, user_id)
        flash('Expense deleted successfully! 🗑️', 'success')
        return redirect(url_for('home'))
        
    except Exception as e:
        flash('An error occurred while deleting the expense. Please try again.', 'error')
        return redirect(url_for('home'))

# ========== DASHBOARD ROUTE ==========

@app.route('/dashboard')
def dashboard():
    """Dashboard with charts and visualizations"""
    if 'user_id' not in session:
        flash('Please login to view the dashboard.', 'info')
        return redirect(url_for('login'))
    
    try:
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
    except Exception as e:
        flash('An error occurred while loading the dashboard. Please try again.', 'error')
        return redirect(url_for('home'))

# ========== EXPORT ROUTES ==========

@app.route('/export/csv')
def export_csv():
    """Export expenses to CSV file"""
    if 'user_id' not in session:
        flash('Please login to export data.', 'info')
        return redirect(url_for('login'))
    
    try:
        import csv
        import io
        from flask import make_response
        
        user_id = session['user_id']
        
        # Get filters from URL
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Get expenses
        expenses = db.get_expenses_by_date_range(user_id, date_from, date_to)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Description', 'Category', 'Amount (₹)'])
        
        # Write data
        for expense in expenses:
            writer.writerow([
                expense['date'],
                expense['description'],
                expense['category'],
                f"{expense['amount']:.2f}"
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=expenses_export.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        flash('Expenses exported successfully! 📥', 'success')
        return response
        
    except Exception as e:
        flash('An error occurred while exporting. Please try again.', 'error')
        return redirect(url_for('home'))

# ========== REPORT ROUTE ==========

@app.route('/report')
def report():
    """Generate summary report"""
    if 'user_id' not in session:
        flash('Please login to view reports.', 'info')
        return redirect(url_for('login'))
    
    try:
        user_id = session['user_id']
        
        # Get report data
        category_summary = db.get_category_summary(user_id)
        monthly_summary = db.get_monthly_summary(user_id)
        stats = db.get_expense_stats(user_id)
        
        # Get current year
        current_year = datetime.now().year
        
        # Get date range for total
        total_expenses = db.get_total_expenses(user_id)
        
        return render_template('report.html',
                             category_summary=category_summary,
                             monthly_summary=monthly_summary,
                             stats=stats,
                             total_expenses=total_expenses,
                             current_year=current_year,
                             username=session.get('username'))
    except Exception as e:
        flash('An error occurred while generating the report. Please try again.', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)