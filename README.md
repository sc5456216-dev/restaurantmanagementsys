# 🍽️ Restaurant Management System

![Django](https://img.shields.io/badge/Django-6.1-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![REST API](https://img.shields.io/badge/REST-API-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A complete Restaurant Management System built with Django and PostgreSQL during my internship at **CodeAlpha**. This system handles all restaurant operations including menu management, table reservations, order processing, inventory tracking, and comprehensive reporting.

---

## ✨ Features

### 📋 Menu Management
- Create and manage categories
- Add/update/delete menu items
- Track item availability
- Manage item pricing and preparation time

### 🪑 Table Management
- Real-time table availability
- Table capacity tracking
- Table status management (Available, Occupied, Reserved, Maintenance)
- Automatic table freeing on order completion

### 📦 Inventory Management
- Track ingredient quantities
- Low stock alerts
- Automated inventory updates on orders
- Stock restocking functionality

### 🧾 Order Processing
- Create orders with multiple items
- Automatic inventory deduction
- Table status updates
- Order status workflow (PENDING → CONFIRMED → PREPARING → READY → SERVED → COMPLETED)
- Order cancellation with inventory reversal

### 📅 Reservations
- Table booking with date/time
- Conflict detection
- Check-in functionality
- Reservation cancellation

### 📊 Reports & Analytics
- Daily sales report
- Revenue analysis
- Stock alerts
- Menu item performance
- Popular items tracking

### 🔐 Admin Panel
- Custom Django admin interface
- Full CRUD operations
- Advanced filtering and search
- Inline editing

---

## 🛠️ Technology Stack

### Backend
- **Django** 6.1 - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** 15 - Database
- **Python** 3.13+

### Tools
- **Postman** - API testing
- **Git** - Version control
- **VS Code** - IDE

### Libraries
- django-cors-headers
- python-decouple
- Pillow

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.13 or higher
- PostgreSQL 15 or higher
- pip (Python package manager)
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/CodeAlpha_Restaurant_management_system.git
cd CodeAlpha_Restaurant_management_system