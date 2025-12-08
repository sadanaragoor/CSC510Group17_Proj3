# 🍔 STACKSHACK CHANGELOG

All notable changes to the StackShack project will be documented in this file.

---

## Version 2.0 - December 2024

### 🎉 Major Release - Complete Feature Enhancement

This is a significant upgrade featuring gamification, advanced payment systems, personalized recommendations, and comprehensive testing with 75%+ code coverage.

### ✨ **New Features**

#### 🏆 Rewards & Loyalty System
- Points system with every purchase
- Tier progression (Bronze → Silver → Gold → Platinum)
- Badges and achievements (First Order, Healthy Eater, Loyal Customer)
- Daily bonus system with streak multipliers
- Weekly challenges for bonus points
- Coupon system for discounts
- Comprehensive rewards dashboard

#### 💳 Payment System
- Multiple payment methods (credit/debit cards, campus cards, digital wallet)
- Campus card integration with student pricing
- Transaction history with search and filtering
- Automatic PDF receipt generation
- Payment analytics dashboard for admins

#### 👤 Profile Management
- Dietary preferences (vegan, gluten-free, high-protein, low-calorie)
- Smart burger recommendations based on preferences
- Email and password management
- Campus card eligibility tracking
- Order history with reorder functionality

#### 📦 Inventory Management
- Real-time stock quantity tracking
- Low stock alerts with customizable thresholds
- Automatic availability updates
- Complete stock history audit trail
- Reorder suggestions based on usage patterns

#### 👨‍💼 Staff Shift Management
- Shift scheduling (Morning, Afternoon, Evening, Night)
- Staff assignments to stations
- Staff profile management
- Weekly shift calendar view
- Performance tracking

#### 🎁 Surprise Box
- Random burgers tailored to dietary preferences
- Budget-based randomization
- Personalized suggestions from order history
- Save and share favorite combinations

### 🧪 **Testing & Quality**
- **493 total test cases** (117 unit + 376 integration)
- **75%+ code coverage** (Models: 97.8%, Services: 78%, Controllers: 70.2%, Routes: 68.7%)
- New test suites: profile, payment, gamification, inventory, staff, services, dietary preferences
- Black formatter configured (line-length: 88)
- Ruff linter configured and passing
- Bandit security scanning
- pytest-cov and pytest-html integration

### 🔧 **Technical Improvements**
- Fixed SQLAlchemy model registration
- SQLite fallback for easy local development
- Enhanced database initialization
- GitHub Actions CI/CD pipeline
- Codecov integration
- Environment-based configuration
- Modular service layer architecture

### 🐛 **Bug Fixes**
- Fixed database table creation for all models
- Resolved pytest collection errors
- Fixed SQLAlchemy connection issues on fresh clones
- Corrected model imports in app initialization
- Fixed linting issues with proper noqa annotations

### 📊 **Project Statistics**
- Lines of Code: 3,242+
- Database Models: 20+
- API Endpoints: 50+
- Controllers: 5
- Services: 5

---

## Version 1.2 - November 6, 2024

### Key Features
- User/Authentication management
- Menu Management
- Create and place custom burger orders
- Track order status

### For Customers
- Browse available menu items
- View nutritional information (calories, protein)
- Custom burger builder

### For Admins
- Full menu management
- User management
- Manage staff/admin accounts
  
### For Staff
- Manage menu ingredients availability and healthy choices
- Manage order status (tracking)

---

## Version 1.1 - November 6, 2024

### Key Features
- User/Authentication management
- Menu Management
- Create and place custom burger orders

### For Customers
- Browse available menu items
- View nutritional information (calories, protein)
- Custom burger builder

### For Admins
- Full menu management
- User management
- Manage staff/admin accounts
  
### For Staff
- Manage menu ingredients availability and healthy choices

---

## Version 1.0 - November 2, 2024

### Initial Release

### Key Features
- User/Authentication management
- Menu Management

### For Customers
- Basic menu browsing

### For Admins
- Full menu management
- User management
- Manage staff/admin accounts
  
### For Staff
- Manage menu ingredients availability and healthy choices

---

**Group 17** • CSC 510 - Software Engineering
