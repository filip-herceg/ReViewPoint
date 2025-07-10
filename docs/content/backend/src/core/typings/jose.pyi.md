# Type Definitions for python-jose JWT Library

## Overview

This module provides TypeScript-style type definitions (`.pyi` file) for the `python-jose` JWT library to improve type safety and IDE support when working with JWT tokens in the ReViewPoint backend.

## Purpose

The `jose.pyi` file serves as a type stub that:

- **Enhances IDE Support**: Provides better autocompletion and type checking for JWT operations
- **Improves Code Safety**: Catches type-related errors at development time
- **Documents API Structure**: Clearly defines the expected structure of JWT headers and claims
- **Supports Static Analysis**: Enables tools like mypy to perform better type checking

## Key Type Definitions

### JWTError Exception
```python
class JWTError(Exception):
    """Exception raised for JWT errors."""
    pass
```

### JWT Headers Structure
```python
class JWTHeaders(TypedDict, total=False):
    alg: str    # Algorithm used for signing
    typ: str    # Token type (typically "JWT")
    kid: str    # Key ID for identifying the signing key
```

### JWT Claims Structure
```python
class JWTClaims(TypedDict, total=False):
    iss: str    # Issuer
    sub: str    # Subject
    aud: str    # Audience
    exp: int    # Expiration time (Unix timestamp)
    # Additional custom claims can be added as needed
```

## Usage in ReViewPoint

This type definition file is automatically used by Python's type checking system when importing from the `jose` library. It provides better type safety for JWT operations in:

- **Authentication Services**: Token generation and validation in `src/services/user.py`
- **Security Utilities**: JWT handling in `src/core/security.py`
- **API Dependencies**: Token verification in `src/api/deps.py`

## Benefits

1. **Type Safety**: Prevents runtime errors by catching type mismatches during development
2. **Better Documentation**: Self-documenting code with clear type annotations
3. **IDE Integration**: Enhanced autocompletion and error detection in IDEs
4. **Maintainability**: Easier to understand and modify JWT-related code

## File Location

```
backend/src/core/typings/jose.pyi
```

This follows Python's standard convention for type stub files, where `.pyi` files provide type information for external libraries or modules that may not have complete type annotations.
