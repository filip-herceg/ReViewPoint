# `models/base.py`

| Item | Value |
|------|-------|
| **Layer** | Models |
| **Responsibility** | Provides the SQLAlchemy declarative base class with common columns and methods |
| **Status** | 🟢 Done |

## 1. Purpose  
This file establishes the foundation for all database models in the application. It defines a common base class that all entity models inherit from, providing consistent ID, timestamp tracking, and serialization capabilities.

## 2. Public API  

| Symbol | Type | Description |
|--------|------|-------------|
| `Base` | DeclarativeBase | SQLAlchemy base class for all models |

**Common Columns on All Models**:
- `id`: Integer primary key, auto-incrementing
- `created_at`: DateTime with automatic creation timestamp
- `updated_at`: DateTime that updates on every record change

**Common Methods**:
- `to_dict()`: Converts model instance to a dictionary
- `__repr__()`: String representation for debugging

## 3. Behaviour & Edge-Cases  

- All models automatically get `id`, `created_at`, and `updated_at` columns
- `created_at` and `updated_at` are set using SQLAlchemy's `func.now()` function:
  - `created_at` is set once at record creation
  - `updated_at` is set at creation and updated with every change
- The `to_dict()` method performs a shallow conversion of model attributes to a dictionary

## 4. Dependencies  

- **Internal**: None

- **External**:
  - `sqlalchemy.orm`: For ORM functionality
  - `sqlalchemy`: For database column types and functions

## 5. Tests  

| Test file | Scenario |
|-----------|----------|
| `backend/tests/models/test_base.py` | Tests for Base.to_dict() and Base.__repr__() methods |

## 6. Open TODOs  
- [ ] Consider adding a `to_json()` method for API responses
- [ ] Add support for relationship serialization in `to_dict()`
- [ ] Add option to exclude certain fields in serialization
