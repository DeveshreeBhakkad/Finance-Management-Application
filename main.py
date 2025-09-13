#!/usr/bin/env python3
"""
Personal Finance Manager (CLI) - main.py
Features:
- User registration & authentication (bcrypt)
- Add/view/delete income & expenses
- Monthly & yearly reports
- Set/view monthly budgets and budget warnings
- Backup & restore SQLite database
"""

import sqlite3
import bcrypt
from datetime import datetime
import shutil
import os
import sys

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
            password BLOB NOT NULL
        )
    """)

    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,          -- Income / Expense
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


# ---------------- Helper Utilities ----------------
def input_nonempty(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Input cannot be empty.")


def parse_float(prompt):
    while True:
        s = input(prompt).strip()
        try:
            return float(s)
        except ValueError:
            print("Invalid number. Please enter a numeric value.")


# ---------------- User Functions ----------------
def register():
    print("\n--- Register ---")
    username = input_nonempty("Enter a username: ")

    # Password entry
    password = input_nonempty("Enter a password: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        print("Username already exists. Try a different one.")
        conn.close()
        return

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()

    print(f"✅ User '{username}' registered successfully!")


def login():
    print("\n--- Login ---")
    username = input_nonempty("Enter username: ")
    password = input_nonempty("Enter password: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode("utf-8"), result[1]):
        print(f"✅ Welcome back, {username}!")
        user_id = result[0]
        user_menu(user_id)
    else:
        print("❌ Invalid username or password.")


# ---------------- Transaction Functions ----------------
def add_transaction(user_id, t_type):
    print(f"\n--- Add {t_type} ---")
    if t_type == "Income":
        category = input_nonempty("Enter income category (e.g., Salary, Bonus, Business): ")
    else:
        category = input_nonempty("Enter expense category (e.g., Food, Rent, Travel): ")

    amount = parse_float("Enter amount: ")
    date = datetime.now().strftime("%Y-%m-%d")

    # If expense, check against budget (warn if exceeded)
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

    print(f"✅ {t_type} of {amount} added under '{category}' on {date}.")


def view_transactions(user_id, filter_type=None):
    """
    filter_type: None (all), "Income", or "Expense"
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if filter_type in ("Income", "Expense"):
        cursor.execute(
            "SELECT id, type, category, amount, date FROM transactions WHERE user_id=? AND type=? ORDER BY date DESC",
            (user_id, filter_type)
        )
    else:
        cursor.execute(
            "SELECT id, type, category, amount, date FROM transactions WHERE user_id=? ORDER BY date DESC",
            (user_id,)
        )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No transactions found.")
    else:
        print("\n--- Transactions ---")
        for row in rows:
            print(f"ID: {row[0]} | {row[1]:7} | {row[2]:15} | {row[3]:8.2f} | {row[4]}")


def delete_transaction(user_id):
    print("\n--- Delete Transaction ---")
    view_transactions(user_id)
    trans_id = input_nonempty("Enter the ID of the transaction to delete: ")
    try:
        trans_id_int = int(trans_id)
    except ValueError:
        print("Invalid ID.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=? AND user_id=?", (trans_id_int, user_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()

    if affected:
        print("✅ Transaction deleted.")
    else:
        print("No matching transaction found.")


# ---------------- Reports Functions ----------------
def monthly_report(user_id):
    print("\n--- Monthly Report ---")
    year = input_nonempty("Enter year (YYYY): ")
    month = input_nonempty("Enter month (MM): ")

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

    income = 0.0
    expenses = 0.0
    for t_type, total in results:
        if t_type == "Income":
            income = total or 0.0
        elif t_type == "Expense":
            expenses = total or 0.0

    savings = (income or 0.0) - (expenses or 0.0)

    print(f"\n📅 Report for {year}-{month}")
    print(f"Total Income  : {income:.2f}")
    print(f"Total Expenses: {expenses:.2f}")
    print(f"Savings       : {savings:.2f}")


def yearly_report(user_id):
    print("\n--- Yearly Report ---")
    year = input_nonempty("Enter year (YYYY): ")

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

    income = 0.0
    expenses = 0.0
    for t_type, total in results:
        if t_type == "Income":
            income = total or 0.0
        elif t_type == "Expense":
            expenses = total or 0.0

    savings = (income or 0.0) - (expenses or 0.0)

    print(f"\n📅 Report for {year}")
    print(f"Total Income  : {income:.2f}")
    print(f"Total Expenses: {expenses:.2f}")
    print(f"Savings       : {savings:.2f}")


# ---------------- Budget Functions ----------------
def set_budget(user_id):
    print("\n--- Set Monthly Budget ---")
    category = input_nonempty("Enter category for budget (e.g., Food, Rent): ")
    amount = parse_float("Enter monthly budget amount: ")
    month = datetime.now().strftime("%Y-%m")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # If budget for same user/category/month exists, update it; else insert
    cursor.execute("""
        SELECT id FROM budgets WHERE user_id=? AND category=? AND month=?
    """, (user_id, category, month))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE budgets SET amount=? WHERE id=?
        """, (amount, existing[0]))
        print(f"✅ Updated budget for '{category}' in {month} to {amount:.2f}.")
    else:
        cursor.execute("""
            INSERT INTO budgets (user_id, category, amount, month) VALUES (?, ?, ?, ?)
        """, (user_id, category, amount, month))
        print(f"✅ Set budget for '{category}' in {month} to {amount:.2f}.")

    conn.commit()
    conn.close()


def view_budgets(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, amount, month FROM budgets WHERE user_id=? ORDER BY month DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No budgets set.")
    else:
        print("\n--- Your Budgets ---")
        for r in rows:
            print(f"ID: {r[0]} | Category: {r[1]:15} | Limit: {r[2]:8.2f} | Month: {r[3]}")


def check_budget(user_id, category, expense_amount, date):
    month = date[:7]  # YYYY-MM
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get budget for this category & month
    cursor.execute("""
        SELECT amount FROM budgets
        WHERE user_id=? AND category=? AND month=?
    """, (user_id, category, month))
    budget = cursor.fetchone()

    if budget:
        budget_limit = budget[0] or 0.0

        # Calculate total spent so far this month for category
        cursor.execute("""
            SELECT SUM(amount) FROM transactions
            WHERE user_id=? AND category=? AND type='Expense' AND strftime('%Y-%m', date)=?
        """, (user_id, category, month))
        total_spent = cursor.fetchone()[0] or 0.0

        projected = total_spent + expense_amount
        if projected > budget_limit:
            print(f"⚠ Warning: This expense will exceed your budget for '{category}'.")
            print(f"  Budget limit : {budget_limit:.2f}")
            print(f"  Spent so far : {total_spent:.2f}")
            print(f"  After adding : {projected:.2f}")

    conn.close()


# ---------------- Backup & Restore ----------------
def backup_data():
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    if not os.path.exists(DB_NAME):
        print("No database found to backup.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_FOLDER, f"finance_backup_{timestamp}.db")

    try:
        shutil.copy(DB_NAME, backup_file)
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print("❌ Backup failed:", e)


def restore_data():
    if not os.path.exists(BACKUP_FOLDER):
        print("No backup folder found.")
        return

    backups = sorted(os.listdir(BACKUP_FOLDER), reverse=True)
    backups = [f for f in backups if f.lower().endswith(".db")]
    if not backups:
        print("No backup files available.")
        return

    print("\n--- Available Backups ---")
    for i, file in enumerate(backups, start=1):
        print(f"{i}. {file}")

    choice = input_nonempty("Enter the number of the backup to restore: ")
    try:
        choice_i = int(choice)
        if not (1 <= choice_i <= len(backups)):
            raise ValueError("Out of range")
        backup_file = os.path.join(BACKUP_FOLDER, backups[choice_i - 1])
        shutil.copy(backup_file, DB_NAME)
        print(f"✅ Database restored from: {backup_file}")
    except Exception as e:
        print("❌ Restore failed or invalid choice.", str(e))


# ---------------- User Menu ----------------
def user_menu(user_id):
    while True:
        print("\n=== Finance Menu ===")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View All Transactions")
        print("4. View Incomes")
        print("5. View Expenses")
        print("6. Delete Transaction")
        print("7. Monthly Report")
        print("8. Yearly Report")
        print("9. Set Budget")
        print("10. View Budgets")
        print("11. Backup Data")
        print("12. Restore Data")
        print("13. Logout")

        choice = input_nonempty("Enter your choice: ")

        if choice == "1":
            add_transaction(user_id, "Income")
        elif choice == "2":
            add_transaction(user_id, "Expense")
        elif choice == "3":
            view_transactions(user_id, None)
        elif choice == "4":
            view_transactions(user_id, "Income")
        elif choice == "5":
            view_transactions(user_id, "Expense")
        elif choice == "6":
            delete_transaction(user_id)
        elif choice == "7":
            monthly_report(user_id)
        elif choice == "8":
            yearly_report(user_id)
        elif choice == "9":
            set_budget(user_id)
        elif choice == "10":
            view_budgets(user_id)
        elif choice == "11":
            backup_data()
        elif choice == "12":
            restore_data()
        elif choice == "13":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")


# ---------------- Main Program ----------------
def main():
    create_tables()
    print("=== Personal Finance Manager ===")
    while True:
        print("\nMain Menu:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input_nonempty("Enter your choice: ")

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Thank you for using Personal Finance Manager! Goodbye.")
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()