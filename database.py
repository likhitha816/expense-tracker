import sqlite3
from datetime import datetime
import auth

# Database file name
DB_NAME = 'expenses.db'

def get_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create all tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Expenses table (with user_id foreign key)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database tables created successfully!")

# ========== USER FUNCTIONS ==========

def create_user(username, email, password):
    """Create a new user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Hash the password
    hashed_password = auth.hash_password(password)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, created_at))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return True, user_id, "User created successfully!"
    except sqlite3.IntegrityError as e:
        conn.close()
        if 'username' in str(e):
            return False, None, "Username already exists"
        elif 'email' in str(e):
            return False, None, "Email already registered"
        return False, None, "Error creating user"

def get_user_by_username(username):
    """Get a user by username"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get a user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return user

def authenticate_user(username, password):
    """Authenticate a user"""
    user = get_user_by_username(username)
    
    if not user:
        return False, None, "User not found"
    
    if auth.verify_password(password, user['password_hash']):
        return True, user['id'], "Login successful!"
    else:
        return False, None, "Invalid password"

# ========== EXPENSE FUNCTIONS (with user_id) ==========

def add_expense(user_id, description, amount, category, date):
    """Add a new expense for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO expenses (user_id, description, amount, category, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, description, amount, category, date))
    
    conn.commit()
    conn.close()
    print("✅ Expense added successfully!")

def get_expenses_by_user(user_id):
    """Get all expenses for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM expenses 
        WHERE user_id = ? 
        ORDER BY date DESC
    ''', (user_id,))
    expenses = cursor.fetchall()
    
    conn.close()
    return expenses

def get_expense_by_id(expense_id, user_id):
    """Get a single expense by ID (verifying it belongs to the user)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM expenses 
        WHERE id = ? AND user_id = ?
    ''', (expense_id, user_id))
    expense = cursor.fetchone()
    
    conn.close()
    return expense

def update_expense(expense_id, user_id, description, amount, category, date):
    """Update an existing expense (verifying it belongs to the user)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE expenses 
        SET description = ?, amount = ?, category = ?, date = ?
        WHERE id = ? AND user_id = ?
    ''', (description, amount, category, date, expense_id, user_id))
    
    conn.commit()
    conn.close()
    print("✅ Expense updated successfully!")

def delete_expense(expense_id, user_id):
    """Delete an expense (verifying it belongs to the user)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM expenses 
        WHERE id = ? AND user_id = ?
    ''', (expense_id, user_id))
    
    conn.commit()
    conn.close()
    print("✅ Expense deleted successfully!")

def get_total_expenses(user_id):
    """Get the total sum of expenses for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(amount) as total 
        FROM expenses 
        WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result['total'] if result['total'] is not None else 0

def get_expenses_by_category(user_id):
    """Get expenses grouped by category for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT category, COUNT(*) as count, SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
    ''', (user_id,))
    categories = cursor.fetchall()
    
    conn.close()
    return categories

def get_today_expenses(user_id):
    """Get today's expenses for a user"""
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM expenses 
        WHERE user_id = ? AND date = ?
        ORDER BY date DESC
    ''', (user_id, today))
    expenses = cursor.fetchall()
    
    conn.close()
    return expenses

def get_today_total(user_id):
    """Get today's total spending for a user"""
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(amount) as total 
        FROM expenses 
        WHERE user_id = ? AND date = ?
    ''', (user_id, today))
    result = cursor.fetchone()
    
    conn.close()
    return result['total'] if result['total'] is not None else 0

# ========== NEW STATS FUNCTIONS FOR CHARTS ==========

def get_monthly_expenses(user_id):
    """Get expenses grouped by month for the last 6 months"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        LIMIT 6
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert to lists for charting
    months = [row['month'] for row in reversed(results)]
    amounts = [row['total'] for row in reversed(results)]
    
    return months, amounts

def get_category_breakdown(user_id):
    """Get expenses broken down by category with colors"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            category,
            SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # Color mapping for categories
    colors = {
        'Food': '#FF6B6B',
        'Transport': '#4ECDC4',
        'Shopping': '#45B7D1',
        'Entertainment': '#96CEB4',
        'Bills': '#FFEAA7',
        'Healthcare': '#DDA0DD',
        'Education': '#98D8C8',
        'Other': '#D3D3D3'
    }
    
    categories = []
    totals = []
    color_list = []
    
    for row in results:
        categories.append(row['category'])
        totals.append(row['total'])
        color_list.append(colors.get(row['category'], '#D3D3D3'))
    
    return categories, totals, color_list

def get_daily_spending_last_7_days(user_id):
    """Get daily spending for the last 7 days"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            date,
            SUM(amount) as total
        FROM expenses
        WHERE user_id = ? 
            AND date >= date('now', '-6 days')
        GROUP BY date
        ORDER BY date
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    days = [row['date'] for row in results]
    amounts = [row['total'] for row in results]
    
    return days, amounts

def get_top_expenses(user_id, limit=5):
    """Get the top N expenses by amount"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            description,
            amount,
            category,
            date
        FROM expenses
        WHERE user_id = ?
        ORDER BY amount DESC
        LIMIT ?
    ''', (user_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    return results


# Initialize the database when this file is imported
if __name__ == '__main__':
    create_tables()