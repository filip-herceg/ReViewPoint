# `test_hashing.py`

| Item | Value |
|------|-------|
| **Layer** | Utility Tests |
| **Responsibility** | Test password hashing and verification utilities |
| **Status** | 🟢 Complete |

## 1. Purpose
This file tests the password hashing and verification functions, ensuring that passwords are securely hashed and can be correctly verified. It also checks for hash uniqueness and negative cases.

## 2. Key Test Scenarios
- Hashing: output is not plain text, uses bcrypt, unique per call
- Verification: correct password matches hash, wrong password does not
- Edge cases: repeated hashing, negative verification

## 3. Notes
- All main password hashing/verification flows are covered.
- Tests are automated and run in CI.
- See the test file for implementation details and specific scenarios.
