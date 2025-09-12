import sqlite3
import bcrypt
from datetime import datetime
import shutil
import os

DB_NAME = "finance.db"
BACKUP_FOLDER = "backups"

# ---------------- Database Setup ----------------
def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,          
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Budgets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# ---------------- User Functions ----------------
def register():
    username = input("Enter a username: ")
    password = input("Enter a password: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        print("Username already exists. Try a different one.")
        conn.close()
        return

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()

    print(f"User {username} registered successfully!")

def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode('utf-8'), result[1]):
        print(f"Welcome back, {username}!")
        user_id = result[0]
        user_menu(user_id)
    else:
        print("Invalid username or password.")

# ---------------- Transaction Functions ----------------
def add_transaction(user_id, t_type):
    if t_type == "Income":
        category = input("Enter income category (e.g., Salary, Bonus, Business): ")
    else:
        category = input("Enter expense category (e.g., Food, Rent, Travel): ")

    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return

    date = datetime.now().strftime("%Y-%m-%d")

    # If expense, check against budget
    if t_type == "Expense":
        check_budget(user_id, category, amount, date)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, type, category, amount, date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, t_type, category, amount, date))
    conn.commit()
    conn.close()

    print(f"{t_type} of {amount} added under {category}.")

def view_transactions(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, category, amount, date FROM transactions WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No transactions found.")
    else:
        print("\n--- Your Transactions ---")
        for row in rows:
            print(f"ID: {row[0]}, {row[1]} - {row[2]}: {row[3]} on {row[4]}")

def delete_transaction(user_id):
    view_transactions(user_id)
    trans_id = input("Enter the ID of the transaction to delete: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=? AND user_id=?", (trans_id, user_id))
    conn.commit()
    conn.close()

    print("Transaction deleted (if it existed).")

# ---------------- Reports Functions ----------------
def monthly_report(user_id):
    year = input("Enter year (YYYY): ")
    month = input("Enter month (MM): ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, SUM(amount) 
        FROM transactions 
        WHERE user_id=? AND strftime('%Y', date)=? AND strftime('%m', date)=?
        GROUP BY type
    """, (user_id, year, month))

    results = cursor.fetchall()
    conn.close()

    income = sum(amount for t_type, amount in results if t_type == "Income")
    expenses = sum(amount for t_type, amount in results if t_type == "Expense")
    savings = income - expenses

    print(f"\n--- Monthly Report ({year}-{month}) ---")
    print(f"Total Income: {income}")
    print(f"Total Expenses: {expenses}")
    print(f"Savings: {savings}")

def yearly_report(user_id):
    year = input("Enter year (YYYY): ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, SUM(amount) 
        FROM transactions 
        WHERE user_id=? AND strftime('%Y', date)=?
        GROUP BY type
    """, (user_id, year))

    results = cursor.fetchall()
    conn.close()

    income = sum(amount for t_type, amount in results if t_type == "Income")
    expenses = sum(amount for t_type, amount in results if t_type == "Expense")
    savings = income - expenses

    print(f"\n--- Yearly Report ({year}) ---")
    print(f"Total Income: {income}")
    print(f"Total Expenses: {expenses}")
    print(f"Savings: {savings}")

# ---------------- Budget Functions ----------------
def set_budget(user_id):
    category = input("Enter category for budget (e.g., Food, Rent): ")
    try:
        amount = float(input("Enter monthly budget amount: "))
    except ValueError:
        print("Invalid amount.")
        return

    month = datetime.now().strftime("%Y-%m")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (user_id, category, amount, month)
        VALUES (?, ?, ?, ?)
    """, (user_id, category, amount, month))
    conn.commit()
    conn.close()

    print(f"Budget of {amount} set for {category} in {month}.")

def view_budgets(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category, amount, month FROM budgets WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No budgets set.")
    else:
        print("\n--- Your Budgets ---")
        for row in rows:
            print(f"Category: {row[0]}, Limit: {row[1]}, Month: {row[2]}")

def check_budget(user_id, category, expense_amount, date):
    month = date[:7]  # YYYY-MM
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT amount FROM budgets
        WHERE user_id=? AND category=? AND month=?
    """, (user_id, category, month))
    budget = cursor.fetchone()

    if budget:
        budget_limit = budget[0]

        cursor.execute("""
            SELECT SUM(amount) FROM transactions
            WHERE user_id=? AND category=? AND type='Expense' AND strftime('%Y-%m', date)=?
        """, (user_id, category, month))
        total_spent = cursor.fetchone()[0] or 0

        if total_spent + expense_amount > budget_limit:
            print(f"⚠ Warning: Adding this expense will exceed your budget for {category} ({budget_limit}).")

    conn.close()

# ---------------- Backup & Restore ----------------
def backup_data():
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_FOLDER, f"finance_backup_{timestamp}.db")

    shutil.copy(DB_NAME, backup_file)
    print(f"✅ Backup created: {backup_file}")

def restore_data():
    if not os.path.exists(BACKUP_FOLDER):
        print("No backup folder found.")
        return

    backups = os.listdir(BACKUP_FOLDER)
    if not backups:
        print("No backup files available.")
        return

    print("\n--- Available Backups ---")
    for i, file in enumerate(backups, start=1):
        print(f"{i}. {file}")

    choice = input("Enter the number of the backup to restore: ")
    try:
        choice = int(choice)
        backup_file = os.path.join(BACKUP_FOLDER, backups[choice - 1])
        shutil.copy(backup_file, DB_NAME)
        print(f"✅ Database restored from {backup_file}")
    except (IndexError, ValueError):
        print("Invalid choice.")

# ---------------- User Menu ----------------
def user_menu(user_id):
    while True:
        print("\n=== Finance Menu ===")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View All Transactions")
        print("4. Delete Transaction")
        print("5. Monthly Report")
        print("6. Yearly Report")
        print("7. Set Budget")
        print("8. View Budgets")
        print("9. Backup Data")
        print("10. Restore Data")
        print("11. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_transaction(user_id, "Income")
        elif choice == "2":
            add_transaction(user_id, "Expense")
        elif choice == "3":
            view_transactions(user_id)
        elif choice == "4":
            delete_transaction(user_id)
        elif choice == "5":
            monthly_report(user_id)
        elif choice == "6":
            yearly_report(user_id)
        elif choice == "7":
            set_budget(user_id)
        elif choice == "8":
            view_budgets(user_id)
        elif choice == "9":
            backup_data()
        elif choice == "10":
            restore_data()
        elif choice == "11":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")

# ---------------- Main Program ----------------
def main():
    create_tables()
    while True:
        print("\n=== Personal Finance Manager ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Thank you for using Personal Finance Manager!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()