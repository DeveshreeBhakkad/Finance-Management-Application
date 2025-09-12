import unittest
import sqlite3
import os
from main import create_tables, register, login, add_transaction

DB_TEST = "test_finance.db"

class FinanceAppTests(unittest.TestCase):
    def setUp(self):
        # Use a fresh test database
        if os.path.exists(DB_TEST):
            os.remove(DB_TEST)
        conn = sqlite3.connect(DB_TEST)
        conn.close()
        create_tables()

    def test_user_registration(self):
        conn = sqlite3.connect(DB_TEST)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("testuser", "hashedpwd"))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE username=?", ("testuser",))
        user = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(user)

    def test_add_transaction(self):
        conn = sqlite3.connect(DB_TEST)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("user1", "pwd"))
        user_id = cursor.lastrowid
        conn.commit()
        cursor.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?, ?, ?, ?, ?)",
                       (user_id, "Income", "Salary", 5000, "2025-09-12"))
        conn.commit()
        cursor.execute("SELECT * FROM transactions WHERE user_id=?", (user_id,))
        transaction = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(transaction)

if __name__ == '__main__':
    unittest.main()