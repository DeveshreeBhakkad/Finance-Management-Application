# 💰 Personal Finance Manager (CLI)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Project-Complete-success)

> “Take control of your money, before it takes control of you.”  

A *Python-based command-line application* to manage your personal finances.  
Track *income, expenses, budgets, and savings, generate **reports, and keep your data safe with **backup & restore features* — all from your terminal.  

---

## ✨ Features

- 🔑 *User Authentication* – Register & login securely (passwords hashed with bcrypt)
- 💵 *Income & Expense Tracking* – Add, view, and delete transactions with categories
- 📊 *Reports* – Generate *Monthly & Yearly summaries* (Income, Expenses, Savings)
- 🎯 *Budgeting* – Set monthly budgets & receive warnings if exceeded
- 💾 *Data Persistence* – All data stored in *SQLite database*
- 🗄 *Backup & Restore* – Create timestamped backups & restore anytime

---

## 📂 Project Structure

finance_manager/
│── main.py          # Main application (run this file)
│── finance.db       # SQLite database (auto-created)
│── backups/         # Backup files stored here
└── README.md        # Documentation

---

## ⚙ Installation & Setup

1. *Clone the repository*
   ```bash
   git clone https://github.com/your-username/finance_manager.git
   cd finance_manager

	2.	Install dependencies

pip install bcrypt


	3.	Run the app

python3 main.py



⸻

🎮 Usage Guide

🔑 Authentication
	•	Register – Create a new account
	•	Login – Access your personal finance dashboard

🏦 Manage Transactions
	•	Add Income (Salary, Bonus, Business, etc.)
	•	Add Expense (Food, Rent, Travel, etc.)
	•	View or Delete transactions
	•	Separate views: All / Incomes / Expenses

📊 Reports
	•	Monthly Report → Enter Year & Month
	•	Yearly Report → Enter Year

🎯 Budgeting
	•	Set a monthly budget per category
	•	⚠ Get warnings when expenses exceed limits

💾 Backup & Restore
	•	Backup creates timestamped copies of your finance.db
	•	Restore lets you recover from any saved backup

⸻

🧩 Example Menu (after login)

=== Finance Menu ===
1. Add Income
2. Add Expense
3. View All Transactions
4. View Incomes
5. View Expenses
6. Delete Transaction
7. Monthly Report
8. Yearly Report
9. Set Budget
10. View Budgets
11. Backup Data
12. Restore Data
13. Logout


⸻

🔒 Security
	•	Passwords are hashed with bcrypt (never stored as plain text)
	•	Each user has a unique account
	•	Backups ensure financial data safety

⸻

🌟 Future Improvements
	•	📄 Export reports as CSV/PDF
	•	👥 Multi-user roles (Admin, Regular User)
	•	🖥 GUI or Web version (Flask/Django)

⸻

