# 💰 Personal Finance Manager (CLI)

> “Take control of your money, before it takes control of you.”  

A *Python-based command-line application* to manage your personal finances.  
Track *income, expenses, budgets, and savings, generate **reports, and keep your data safe with **backup & restore features* — all from your terminal.  

---

## 🚀 Features

- 🔑 *User Authentication* – Secure registration & login (bcrypt password hashing)
- 💵 *Income & Expense Tracking* – Add, view, and delete transactions
- 📊 *Reports* – Monthly & yearly financial summaries (income, expenses, savings)
- 🎯 *Budgeting* – Set monthly budgets & get alerts when exceeded
- 💾 *Data Persistence* – SQLite database with Backup & Restore
- 🧪 *Testing* – Unit tests for stability & correctness

---

## 📂 Project Structure

finance_manager/
│── main.py          # Main application
│── finance.db       # SQLite database (auto-created)
│── backups/         # Backup files stored here
│── tests/
│   └── test_app.py  # Unit tests
└── README.md        # Documentation


## ⚙ Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/DeveshreeBhakkad/Finance-Management-Application.git
   cd finance_manager

   2.	Install dependencies:
   pip install bcrypt

   3.	Run the app:
   python3 main.py

   🎮 Usage Guide

🔑 Authentication
	•	Register – Create a new account
	•	Login – Access your personal finance dashboard

🏦 Manage Transactions
	•	Add Income or Expense (with categories)
	•	View all transactions
	•	Delete transactions

📊 Reports
	•	Monthly Report → Enter Year + Month
	•	Yearly Report → Enter Year

🎯 Budgeting
	•	Set a monthly budget per category
	•	⚠ Get warnings when expenses exceed limits

💾 Backup & Restore
	•	Backup creates timestamped copies of finance.db
	•	Restore from any previous backup

⸻

🧪 Running Tests

Run all tests inside the tests/ folder:
🔒 Security
	•	Passwords are hashed with bcrypt (never stored in plain text)
	•	User accounts are unique and isolated
	•	Backup system ensures data safety

⸻

🌟  Future Improvements
	•	📄 Export reports as PDF/CSV
	•	👥 Multi-user roles (admin, regular user)
	•	🖥 GUI/Web version with Flask or Django

⸻





