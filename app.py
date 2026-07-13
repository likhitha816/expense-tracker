from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import database as db

app = Flask(__name__)

# Initialize the database
db.create_table()

@app.route('/')
def home():
    """Home page - shows all expenses"""
    expenses = db.get_all_expenses()
    total = db.get_total_expenses()
    categories = db.get_expenses_by_category()
    today_total = db.get_today_total()
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('index.html', 
                         expenses=expenses, 
                         total=total,
                         categories=categories,
                         today_total=today_total,
                         today=today)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    """Add a new expense"""
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        
        db.add_expense(description, amount, category, date)
        return redirect(url_for('home'))
    
    return render_template('add.html')

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    """Edit an existing expense"""
    expense = db.get_expense_by_id(expense_id)
    
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        
        db.update_expense(expense_id, description, amount, category, date)
        return redirect(url_for('home'))
    
    return render_template('edit.html', expense=expense)

@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    """Delete an expense"""
    db.delete_expense(expense_id)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)