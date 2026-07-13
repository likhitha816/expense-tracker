import sqlite3
from datetime import datetime

# Database file name
DB_NAME = 'expenses.db'

def get_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def create_table():
    """Create the expenses table if it doesn't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database table created successfully!")

def add_expense(description, amount, category, date):
    """Add a new expense to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO expenses (description, amount, category, date)
        VALUES (?, ?, ?, ?)
    ''', (description, amount, category, date))
    
    conn.commit()
    conn.close()
    print("✅ Expense added successfully!")

def get_all_expenses():
    """Get all expenses from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
    expenses = cursor.fetchall()
    
    conn.close()
    return expenses

def get_expense_by_id(expense_id):
    """Get a single expense by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
    expense = cursor.fetchone()
    
    conn.close()
    return expense

def update_expense(expense_id, description, amount, category, date):
    """Update an existing expense"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE expenses 
        SET description = ?, amount = ?, category = ?, date = ?
        WHERE id = ?
    ''', (description, amount, category, date, expense_id))
    
    conn.commit()
    conn.close()
    print("✅ Expense updated successfully!")

def delete_expense(expense_id):
    """Delete an expense by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    
    conn.commit()
    conn.close()
    print("✅ Expense deleted successfully!")

def get_total_expenses():
    """Get the total sum of all expenses"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT SUM(amount) as total FROM expenses')
    result = cursor.fetchone()
    
    conn.close()
    return result['total'] if result['total'] is not None else 0

def get_expenses_by_category():
    """Get expenses grouped by category"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT category, COUNT(*) as count, SUM(amount) as total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    ''')
    categories = cursor.fetchall()
    
    conn.close()
    return categories

def get_today_expenses():
    """Get today's expenses"""
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM expenses 
        WHERE date = ? 
        ORDER BY date DESC
    ''', (today,))
    expenses = cursor.fetchall()
    
    conn.close()
    return expenses

def get_today_total():
    """Get today's total spending"""
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(amount) as total 
        FROM expenses 
        WHERE date = ?
    ''', (today,))
    result = cursor.fetchone()
    
    conn.close()
    return result['total'] if result['total'] is not None else 0

# Initialize the database when this file is imported
if __name__ == '__main__':
    create_table()