# `test_base.py`

| Item               | Value                                                           |
| ------------------ | --------------------------------------------------------------- |
| **Layer**          | Model Tests                                                     |
| **Responsibility** | Test the Base class functionality like to_dict() and **repr**() |
| **Status**         | 🟢 Complete                                                     |

## 1. Purpose

This file tests the SQLAlchemy Base class used by all models, ensuring that helper methods like `to_dict()` and `__repr__()` work as expected for serialization and debugging.

## 2. Key Test Scenarios

- `to_dict()`: correct serialization of model attributes
- `__repr__()`: provides useful debugging output
- Edge cases: empty models, models with various field types

## 3. Notes

- Ensures a consistent interface for all models.
- Tests are automated and run in CI.
- See the test file for implementation details and specific scenarios.

## 4. Test-by-Test Coverage (Detailed)

### `test_base_to_dict`

- **Setup:** Defines a `DummyToDict` model inheriting from `Base` with `id` and `name` fields, and a custom `to_dict()` method for test purposes.
- **Action:** Instantiates the dummy, sets its fields, and calls `to_dict()`.
- **Assertion:** Asserts that the resulting dictionary contains the expected keys (`id`, `name`).
- **Purpose:** Verifies that the `to_dict()` method on a model correctly serializes its attributes to a dictionary, ensuring a consistent serialization interface for all models.

### `test_base_repr`

- **Setup:** Defines a `DummyRepr` model inheriting from `Base` with `id` and `name` fields.
- **Action:** Instantiates the dummy, sets its `id`, and calls `repr()`.
