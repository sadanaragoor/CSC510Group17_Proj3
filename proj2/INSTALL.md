# 🍔 StackShack v2.0 - Installation Guide

Complete installation guide for **StackShack** - the custom burger ordering system with gamification, smart recommendations, and comprehensive features.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **MySQL 8.0+ or SQLite** - [Download MySQL](https://dev.mysql.com/downloads/mysql/) (MySQL optional - SQLite works out of the box)
- **Git** - [Download Git](https://git-scm.com/downloads)

---

## 📦 Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/sadanaragoor/CSC510Group17_Proj3.git
cd CSC510Group17_Proj3/proj2/stackshack
```

### 2. Set Up Virtual Environment

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

---

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs all required packages including:
- Flask 3.0.0
- Flask-SQLAlchemy
- Flask-Login
- PyMySQL
- pytest & pytest-cov
- Black & Ruff
- ReportLab (for PDF receipts)

---

### 4. Configure Database

You have **two options**: SQLite (quick start) or MySQL (production).

#### **Option A: SQLite (Recommended for Development) 🚀**

**No configuration needed!** SQLite is automatically used if MySQL credentials are not provided.

Simply skip to step 5 - the app will create a `stackshack_dev.db` file automatically.

#### **Option B: MySQL (Production)**

1. **Create MySQL Database:**
```sql
CREATE DATABASE stackshack;
USE stackshack;
```

2. **Create `.env` file** in `proj2/stackshack/`:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# MySQL Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=stackshack
```

**Or use direct DATABASE_URL:**
```env
DATABASE_URL=mysql+pymysql://root:password@localhost/stackshack
```

**Important:** Replace `your_mysql_password` with your actual MySQL password!

---

### 5. Initialize the Database
```bash
python create_tables.py
```

This creates all necessary tables:
- **User tables** (users, authentication)
- **Menu tables** (items, categories, stock)
- **Order tables** (orders, order items)
- **Payment tables** (transactions, campus cards, receipts, wallets)
- **Gamification tables** (points, badges, challenges, coupons, punch cards)
- **Shift tables** (staff profiles, shifts, assignments)

You should see:
```
✅ All tables created successfully!
✅ 20+ models registered
```

---

### 6. Create Admin User
```bash
python create_admin.py
```

This creates an admin account:
- **Username:** `admin`
- **Password:** `admin`

⚠️ **Change this password after first login!**

---

### 7. Seed Sample Menu Data
```bash
python seed_menu.py
```

This populates the menu with sample burger ingredients:
- Buns (Sesame, Whole Wheat, Brioche)
- Patties (Beef, Chicken, Veggie, Beyond Meat)
- Toppings (Lettuce, Tomato, Onions, Pickles)
- Sauces (Ketchup, Mayo, BBQ, Special Sauce)
- Cheese (Cheddar, Swiss, American)

---

## 🎮 Running the Application

### Start the Server
```bash
python app.py
```

**Or using Flask CLI:**
```bash
export FLASK_APP=app.py  # On Mac/Linux
# or
$env:FLASK_APP="app.py"  # On Windows PowerShell

flask run
```

You should see:
```
Database tables checked/created.
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```
or
```
http://127.0.0.1:5000
```

---

## ✅ Verify Installation

### 1. Test Database Connection
```bash
python test_conn.py
```

Expected output: `Connected successfully!` (SQLite or MySQL)

### 2. Run Test Suite
```bash
pytest
```

Expected: **493 tests passed** ✅

### 3. Check Code Coverage
```bash
pytest --cov=models --cov=controllers --cov=routes --cov=services
```

Expected: **75%+ coverage** ✅

---

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov=models --cov=controllers --cov=routes --cov=services --cov-report=term --cov-report=html
```

### Run Specific Test Suites
```bash
# Profile tests
pytest tests/profileTests/

# Payment tests
pytest tests/paymentTests/

# Gamification tests
pytest tests/rewardsTests/

# Service tests
pytest tests/servicesTests/
```

### Generate HTML Test Report
```bash
pytest --html=test-results.html --self-contained-html
```

---

## 🛠️ Development Tools

### Code Formatting
```bash
# Format all code with Black
black .

# Check formatting without changes
black --check .
```

### Linting
```bash
# Run Ruff linter
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Security Scanning
```bash
# Run Bandit security scan
bandit -r . -ll

# Check for vulnerabilities
pip-audit
```

---

## 🐛 Troubleshooting

### Issue: "Table doesn't exist" errors

**Solution:** Run `python create_tables.py` to ensure all models are imported and tables created.

### Issue: Port 5000 already in use

**Solution:** Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Issue: ModuleNotFoundError

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Can't connect to MySQL

**Solution:** Use SQLite by removing all `DB_*` variables from `.env`. The app will automatically use SQLite.

### Issue: Virtual environment not activating (Windows)

**Solution:**
```powershell
# Enable script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📚 Next Steps

After successful installation:

1. **Login as admin** (`admin` / `admin`)
2. **Create additional users** from the admin dashboard
3. **Customize menu items** via menu management
4. **Configure gamification** settings and challenges
5. **Set up staff shifts** for your restaurant
6. **Test payment flows** with campus cards and wallets

---

## 📦 Database Fallback Priority

The application uses databases in this order:
1. `DATABASE_URL` environment variable (if set)
2. MySQL with `DB_*` environment variables (if all are set)
3. **SQLite** (`stackshack_dev.db`) as automatic fallback

---

## 🔧 Configuration Files

- **`.env`** - Environment variables (create from template above)
- **`config.py`** - Application configuration (Development, Testing, Production)
- **`pyproject.toml`** - Black & Ruff configuration
- **`pytest.ini`** - Pytest configuration
- **`requirements.txt`** - Python dependencies

---

## 📊 What Gets Installed

- **493 test cases** (117 unit + 376 integration)
- **20+ database models**
- **50+ API endpoints**
- **5 controllers** (auth, menu, order, payment, status)
- **5 services** (recommendations, gamification, challenges, payment, shifts)
- **Complete test coverage** (75%+)

---

## 💡 Tips

- Use **SQLite** for quick local development
- Use **MySQL** for production deployments
- Run tests frequently: `pytest`
- Format code before commits: `black .`
- Check linting: `ruff check .`
- Maintain 75%+ test coverage

---

**Installation complete!** 🎉

For more information, see the [README.md](README.md) or [CONTRIBUTING.md](CONTRIBUTING.md).

---

**Group 17** • CSC 510 - Software Engineering
