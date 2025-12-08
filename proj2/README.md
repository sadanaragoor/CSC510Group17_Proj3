
# 🍔 StackShack - Build Your Own Burger! (Version 2.0)

<div align="center">

[![Tests](https://github.com/sadanaragoor/CSC510Group17_Proj3/actions/workflows/tests.yml/badge.svg)](https://github.com/sadanaragoor/CSC510Group17_Proj3/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/sadanaragoor/CSC510Group17_Proj3/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/sadanaragoor/CSC510Group17_Proj3)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/mysql-8.0-blue.svg)](https://www.mysql.com/)

[![License](https://img.shields.io/badge/license-Educational-blue.svg)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/sadanaragoor/CSC510Group17_Proj3)](https://github.com/sadanaragoor/CSC510Group17_Proj3/commits/main)
[![Issues](https://img.shields.io/github/issues/sadanaragoor/CSC510Group17_Proj3)](https://github.com/sadanaragoor/CSC510Group17_Proj3/issues)

[![Closed Issues](https://img.shields.io/github/issues-closed/sadanaragoor/CSC510Group17_Proj3)](https://github.com/sadanaragoor/CSC510Group17_Proj3/issues?q=is%3Aissue+is%3Aclosed)

[![Contributors](https://img.shields.io/github/contributors/sadanaragoor/CSC510Group17_Proj3)](https://github.com/sadanaragoor/CSC510Group17_Proj3/graphs/contributors)


[![DOI](https://zenodo.org/badge/1098759280.svg)](https://doi.org/10.5281/zenodo.17853408)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: Ruff](https://img.shields.io/badge/Linter-Ruff-blue)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![vulnerabilities: pip-audit](https://img.shields.io/badge/vulnerabilities-pip--audit-blue.svg)](https://pypi.org/project/pip-audit/)

**Group 17** • CSC 510 - Software Engineering

*Build your perfect custom burger with personalized recommendations, gamification rewards, and seamless payment!*

[Features](#-key-features) • [Installation](#installation) • [Usage](#usage) • [Testing](#running-the-test-suite) • [API](#api-references)

</div>

---

## 🍔 StackShack! Who are we?

Feeling overwhelmed by campus dining options? StackShack makes it fun, fast and easy. Customize every layer of your burger—from buns to sauces, toppings to patties — with **personalized recommendations** based on your dietary preferences. Earn points, unlock badges, complete challenges, and enjoy a gamified dining experience!

*Free and open source for educational use*

## ✨ Why You'll Love Us

- 🎯 **Smart Recommendations** - Get personalized burger suggestions based on your dietary preferences (vegan, gluten-free, high-protein, low-calorie)
- 🎮 **Gamification** - Earn points, unlock badges, complete daily/weekly challenges, and redeem coupons
- 💳 **Flexible Payments** - Pay with campus cards, credit/debit cards, or digital wallet
- 👤 **Profile Management** - Set dietary preferences, update email, manage your password
- 📊 **Order Tracking** - Watch your order progress from kitchen to tray with real-time status updates
- 🎁 **Surprise Box** - Get random burgers tailored to your nutritional preferences
- 📦 **Inventory Management** - Real-time ingredient availability tracking
- 👨‍💼 **Staff Management** - Complete shift scheduling and assignment system
- 🧾 **Receipt Generation** - Automatic PDF receipt generation for every order

Are you a developer? Our **FLASK + MySQL/SQLite** based application is easy to use, easy to maintain, lightweight, scalable, modular and clean!

---

## 🎯 Key Features

### 🎮 Gamification System (NEW!)
- **Points & Rewards** - Earn points with every purchase and redeem for discounts
- **Badges & Achievements** - Unlock badges for milestones (first order, healthy eater, etc.)
- **Daily Bonuses** - Claim daily points for consecutive logins
- **Weekly Challenges** - Complete challenges like "Order 3 healthy burgers this week"
- **Punch Cards** - Traditional loyalty cards for free items
- **Coupons** - Redeem discount coupons at checkout

### 💳 Payment System (NEW!)
- **Multiple Payment Methods** - Credit/debit cards, campus cards, digital wallet
- **Campus Card Integration** - Special pricing and balance management for students
- **Transaction History** - Complete payment history with receipts
- **Receipt Generation** - Automatic PDF receipts for all transactions
- **Balance Management** - Add funds to digital wallet
- **Admin Dashboard** - Payment analytics and transaction monitoring

### 👤 Profile Management (NEW!)
- **Dietary Preferences** - Set vegan, gluten-free, high-protein, low-calorie preferences
- **Smart Recommendations** - Get burger recommendations based on your preferences
- **Email Management** - Update email and check campus card eligibility
- **Password Management** - Secure password updates
- **Order History** - View past orders and reorder favorites

### 📦 Inventory Management (NEW!)
- **Stock Tracking** - Real-time ingredient quantity monitoring
- **Low Stock Alerts** - Automatic alerts when items run low
- **Availability Management** - Enable/disable items based on stock
- **Stock History** - Track inventory changes over time

### 👨‍💼 Staff Shift Management (NEW!)
- **Shift Scheduling** - Create and manage staff shifts (Morning, Afternoon, Evening, Night)
- **Staff Assignments** - Assign staff to specific shifts and stations
- **Staff Profiles** - Manage staff information and positions
- **Shift Calendar** - Weekly shift calendar view

### 🎁 Surprise Box (NEW!)
- **Random Burgers Tailored to Your Taste** - Get adventurous with personalized random burger combinations
- **Dietary Compliance** - All surprise boxes respect your dietary preferences and restrictions
- **Personalized Randomization** - Random burgers that match your vegan, gluten-free, high-protein, or low-calorie settings
- **Budget Options** - Set your preferred price range for surprise burgers
- **Nutritional Balance** - Smart algorithm ensures balanced macro distribution
- **Taste Profile Learning** - System learns from your order history for better suggestions
- **Adventurous Mode** - Try new ingredient combinations you haven't ordered before
- **Save & Share** - Save favorite surprise burgers and share your creations with friends

### 🍔 Core Features
- **User Management** - Role-based access (customer, staff, admin) with secure authentication
- **Order Purchase** - Interactive burger builder with real-time pricing and visual feedback
- **Order Management** - Real-time order tracking and status updates
- **Menu Management** - Complete CRUD operations for menu items
- **Status Tracking** - Live order status from pending to delivered
- **Nutritional Info** - Calorie and protein information for health-conscious users

---

## 🏗️ Tech Stack

**Backend:**
- Python 3.8+
- Flask 3.0.0
- Flask-SQLAlchemy (ORM)
- Flask-Login (Authentication)
- MySQL 8.0+ / SQLite (development)
- ReportLab (PDF generation)

**Frontend:**
- HTML5
- CSS3
- JavaScript
- Jinja2 Templates
- Responsive Design

**Testing & Quality:**
- pytest (493 test cases: 117 unit, 376 integration)
- pytest-cov (75%+ code coverage)
- pytest-html (HTML test reports)
- Black (code formatting)
- Ruff (linting)
- Bandit (security scanning)

**CI/CD:**
- GitHub Actions
- Codecov Integration
- Automated Testing & Linting

---

## 📊 Test Coverage

Our comprehensive test suite includes:
- **Total Test Cases**: 493
  - Unit Tests: 117
  - Integration Tests: 376
- **Code Coverage**: 75%+
  - Models: 99%
  - Controllers: 77%
  - Routes: 83%
  - Services: 92%

All tests are automatically run on every push via GitHub Actions with coverage reporting to Codecov.

---

## 🎮 Who Can Use StackShack?

### 👥 For Customers
- Browse personalized burger recommendations
- View nutritional information (calories, protein)
- Custom burger builder with real-time pricing
- Earn points, badges, and complete challenges
- Manage dietary preferences and profile
- Track orders in real-time
- Pay with multiple payment methods
- View transaction history and receipts

### 👨‍💼 For Staff
- Manage ingredient availability and stock
- Update order statuses through workflow
- View assigned shifts and stations
- Access staff dashboard
- Update menu item healthy choices

### 🔧 For Admins
- Full menu management (CRUD operations)
- User role management
- Staff shift scheduling and assignments
- Payment analytics dashboard
- Gamification settings (challenges, rewards)
- System-wide inventory oversight
- Receipt and transaction management

---

## 📁 Project Structure

```bash
stackshack/
├── controllers/              # Business logic layer
│   ├── auth_controller.py
│   ├── menu_controller.py
│   ├── order_controller.py
│   ├── payment_controller.py
│   └── status_controller.py
├── database/                 # Database configuration
│   └── db.py
├── models/                   # Database models (SQLAlchemy)
│   ├── user.py
│   ├── menu_item.py
│   ├── order.py
│   ├── payment.py           # NEW: Payment models
│   ├── gamification.py      # NEW: Gamification models
│   └── shift.py             # NEW: Shift management models
├── routes/                   # URL routing (Flask Blueprints)
│   ├── auth_routes.py
│   ├── menu_routes.py
│   ├── order_routes.py
│   ├── payment_routes.py    # NEW: Payment endpoints
│   ├── profile_routes.py    # NEW: Profile management
│   ├── gamification_routes.py  # NEW: Gamification endpoints
│   ├── shift_routes.py      # NEW: Shift management
│   ├── status_routes.py
│   └── surprise_routes.py
├── services/                 # Service layer
│   ├── burger_recommendations.py  # NEW: Recommendation engine
│   ├── challenge_service.py       # NEW: Challenge logic
│   ├── gamification_service.py    # NEW: Points & rewards
│   ├── payment_gateway.py         # NEW: Payment processing
│   └── shift_service.py           # NEW: Shift scheduling
├── templates/                # HTML templates
│   ├── menu/
│   ├── orders/
│   ├── payment/             # NEW: Payment templates
│   ├── profile/             # NEW: Profile templates
│   ├── gamification/        # NEW: Rewards templates
│   ├── shifts/              # NEW: Shift templates
│   └── ...
├── tests/                    # Comprehensive test suite (493 tests)
│   ├── controllersTests/
│   ├── dietaryPreferencesTests/   # NEW
│   ├── inventoryTests/            # NEW
│   ├── LoginManagementTests/
│   ├── menuManagementTests/
│   ├── paymentTests/              # NEW
│   ├── profileTests/              # NEW
│   ├── purchaseManagementTests/
│   ├── rewardsTests/              # NEW
│   ├── routesTests/
│   ├── servicesTests/             # NEW
│   ├── staffManagementTests/      # NEW
│   ├── statusManagementTests/
│   └── surpriseBoxTests/
├── static/                   # Static assets (images, CSS)
├── .github/workflows/        # CI/CD configuration
│   └── tests.yml            # Automated testing & coverage
├── app.py                    # Main application entry point
├── config.py                 # Configuration settings
├── create_tables.py          # Database initialization
├── create_admin.py          # Admin user creation
├── seed_menu.py             # Sample data seeding
├── pyproject.toml           # Black & Ruff configuration
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **MySQL 8.0+ or SQLite** - [Download MySQL](https://dev.mysql.com/downloads/mysql/) (optional for local dev)
- **Git** - [Download Git](https://git-scm.com/downloads)

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

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database

**Option A: SQLite (Quick Start - No Setup Required)**

SQLite is automatically used if no MySQL credentials are provided. Perfect for local development!

**Option B: MySQL (Production)**

1. Create MySQL database:
```sql
CREATE DATABASE stackshack;
USE stackshack;
```

2. Create `.env` file in `proj2/stackshack/`:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# MySQL Configuration (optional - omit to use SQLite)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=stackshack
```

### 5. Initialize Database
```bash
python create_tables.py
```

This creates all tables including:
- Users, Menu Items, Orders
- Payment tables (transactions, campus cards, receipts)
- Gamification tables (points, badges, challenges, coupons)
- Shift management tables

### 6. Create Admin User
```bash
python create_admin.py
```

Creates admin account:
- **Username:** `admin`
- **Password:** `admin`

⚠️ **Change this password after first login!**

### 7. Seed Sample Data
```bash
python seed_menu.py
```

Populates menu with burger ingredients.

---

## 🎮 Running the Application

### Start the Server
```bash
python app.py
```

You should see:
```
Database tables checked/created.
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### Access the Application

Open your browser:
```
http://localhost:5000
```

---

## 🧪 Running the Test Suite

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=models --cov=controllers --cov=routes --cov=services --cov-report=term --cov-report=html
```

### Generate HTML Test Report
```bash
pytest --html=test-results.html --self-contained-html
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

### Code Quality Checks
```bash
# Format code with Black
black .

# Lint with Ruff
ruff check .

# Security scan with Bandit
bandit -r . -ll

# Check for vulnerabilities
pip-audit
```

---

## 📖 Usage Examples

### Customer Journey

1. **Register & Login**
   - Navigate to `/auth/register`
   - Create account
   - Set dietary preferences in profile

2. **Get Personalized Recommendations**
   - View dashboard with burger recommendations
   - Recommendations match your dietary preferences

3. **Build & Order a Burger**
   - Go to `/orders/new`
   - Select ingredients
   - View real-time price calculation
   - Place order

4. **Pay for Order**
   - Choose payment method (card/campus card/wallet)
   - Complete payment
   - Receive PDF receipt

5. **Earn Rewards**
   - Earn points automatically
   - Claim daily bonus
   - Complete weekly challenges
   - Unlock badges
   - Redeem coupons

6. **Track Order**
   - View order status in real-time
   - Get notified when ready for pickup

### Admin Dashboard

1. **Menu Management**
   - Add/edit/delete menu items
   - Manage inventory and stock levels
   - Toggle availability
   - Mark healthy choices

2. **Staff Management**
   - Create staff accounts
   - Schedule shifts
   - Assign staff to stations

3. **Payment Analytics**
   - View transaction history
   - Monitor payment methods
   - Generate financial reports

4. **Gamification Settings**
   - Create challenges
   - Manage reward tiers
   - Issue coupons

---

## 🔌 API References

### Authentication Endpoints

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/auth/register` | GET, POST | Register new user | Public |
| `/auth/login` | GET, POST | User login | Public |
| `/auth/logout` | GET | User logout | Authenticated |
| `/auth/dashboard` | GET | User dashboard with recommendations | Authenticated |

### Profile Endpoints (NEW)

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/profile/profile` | GET | View user profile | Authenticated |
| `/profile/update-email` | POST | Update user email | Authenticated |
| `/profile/update-password` | POST | Update user password | Authenticated |
| `/profile/update-preferences` | POST | Update dietary preferences | Authenticated |

### Payment Endpoints (NEW)

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/payment/checkout` | GET, POST | Process payment | Authenticated |
| `/payment/history` | GET | View payment history | Authenticated |
| `/payment/campus-card` | GET, POST | Manage campus card | Authenticated |
| `/payment/add-balance` | POST | Add wallet balance | Authenticated |
| `/payment/admin-dashboard` | GET | Payment analytics | Admin |

### Gamification Endpoints (NEW)

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/gamification/rewards` | GET | View rewards dashboard | Authenticated |
| `/gamification/claim-daily` | POST | Claim daily bonus | Authenticated |
| `/gamification/redeem` | POST | Redeem coupon | Authenticated |

### Menu Endpoints

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/menu/items` | GET | View all items | Staff/Admin |
| `/menu/items/create` | POST | Create menu item | Staff/Admin |
| `/menu/items/<id>/edit` | GET, POST | Edit menu item | Staff/Admin |
| `/menu/items/<id>/delete` | POST | Delete menu item | Admin |
| `/menu/browse-ingredients` | GET | Browse ingredients | Public |

### Order Endpoints

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/orders/new` | GET, POST | Create new order | Authenticated |
| `/orders/history` | GET | View order history | Authenticated |
| `/orders/ingredients/<category>` | GET | Get ingredients by category | Public |

### Shift Management Endpoints (NEW)

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/shifts/admin-dashboard` | GET | Shift management dashboard | Admin |
| `/shifts/staff-dashboard` | GET | View assigned shifts | Staff |
| `/shifts/assign` | POST | Assign shift to staff | Admin |

---

## 🛠️ Configuration

### Environment Variables

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration (optional for SQLite)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=stackshack

# Or use direct DATABASE_URL
DATABASE_URL=mysql+pymysql://user:pass@host/db
```

### Database Fallback

The application automatically uses:
1. `DATABASE_URL` if set
2. MySQL with `DB_*` variables if all are set
3. SQLite (`stackshack_dev.db`) as fallback for local development

---

## 🐛 Troubleshooting

### SQLAlchemy Errors

**Problem:** "Table doesn't exist" errors for payment/gamification features

**Solution:** Run `python create_tables.py` to ensure all models are imported and tables created.

### Port Already in Use

**Problem:** Port 5000 is taken

**Solution:** Change port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Module Not Found

**Problem:** `ModuleNotFoundError`

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Connection Failed

**Problem:** Can't connect to MySQL

**Solution:** Use SQLite by removing all `DB_*` variables from `.env`. The app will automatically use SQLite.

---

## 🔒 Security

- ✅ Password hashing with bcrypt
- ✅ CSRF protection on all forms
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ Session management with Flask-Login
- ✅ Input validation and sanitization
- ✅ Role-based access control
- ✅ Secure payment processing
- ✅ Environment variable protection

**Security Best Practices:**
- Never commit `.env` file
- Change default admin password
- Use strong passwords
- Keep dependencies updated
- Regular security audits with Bandit

---

## 📝 Code Quality

### Standards
- ✅ PEP 8 compliance
- ✅ Black formatting (line length: 88)
- ✅ Ruff linting
- ✅ Type hints where applicable
- ✅ Comprehensive docstrings
- ✅ Modular architecture
- ✅ 75%+ test coverage

### Pre-commit Checks
```bash
# Format code
black .

# Lint code
ruff check .

# Run tests
pytest

# Check coverage
pytest --cov=models --cov=controllers --cov=routes --cov=services
```

---

## 🎓 Educational Use

This project is developed for **CSC 510 - Software Engineering** and demonstrates:

- ✅ RESTful API design
- ✅ MVC architecture
- ✅ Database modeling with ORM
- ✅ User authentication & authorization
- ✅ Test-driven development (TDD)
- ✅ Continuous Integration (CI/CD)
- ✅ Code quality tools
- ✅ Modular design patterns
- ✅ Service layer architecture
- ✅ Payment gateway integration concepts
- ✅ Gamification systems

---

## 📜 License

This project is for educational purposes as part of CSC 510. No trademark claims.

---

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting)
2. Check [GitHub Issues](https://github.com/sadanaragoor/CSC510Group17_Proj3/issues)
3. Contact the team

---

## 👥 Team

**Group 17 - CSC 510 Software Engineering**

Project maintained by contributors. All team members share roles:
- Project Maintainers
- Core Developers
- Code Reviewers
- Documentation Writers
- QA Testers

No external funding received.

---

## 📊 Project Stats

- **Lines of Code**: 3,242+ (application code)
- **Test Cases**: 493 (117 unit + 376 integration)
- **Code Coverage**: 75%+
- **Models**: 20+ database models
- **Routes**: 50+ API endpoints
- **Controllers**: 5 business logic controllers
- **Services**: 5 service modules
- **Total Commits**: 100+

---

**Happy Stacking! 🍔**

*Built with ❤️ by Group 17 for CSC 510*

