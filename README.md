# NexusERP

A Flask-based Manufacturing ERP System for small-to-medium manufacturing businesses.

## Features

- **Products & Inventory** - Full product lifecycle with stock tracking
- **Sales Orders** - Customer management, order creation, confirmation, and delivery
- **Purchase Orders** - Vendor management, PO creation, confirmation, and receiving
- **Bill of Materials** - Multi-level BOMs with component tracking
- **Manufacturing** - Manufacturing Orders with production tracking
- **Procurement Automation** - MTS/MTO rules engine
- **Point of Sale** - POS terminal with session management
- **Analytics & Reports** - KPI dashboard with Chart.js visualizations
- **Audit Logging** - Full activity tracking
- **RBAC** - Role-based access control

## Quick Start

```bash
# Install uv
pip install uv

# Sync dependencies
uv sync

# Initialize the database
uv run flask shell -c "from app.extensions import db; db.create_all()"

# Seed demo data
uv run flask shell -c "from app.seed.demo_data import seed_demo_data; seed_demo_data()"

# Run the application
uv run flask run
```

Default credentials: admin / admin123

## Tech Stack

- Python 3.14, Flask 3.1, SQLAlchemy, Bootstrap 5
- Flask-Login, Flask-Migrate, Flask-SocketIO
- Chart.js, SQLite (dev) / PostgreSQL (prod)
