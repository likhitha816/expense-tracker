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

# Initialize the database when this file is imported
if __name__ == '__main__':
    create_tables()