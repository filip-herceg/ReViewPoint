# ReViewPoint Backend Documentation

Welcome to the detailed documentation for the ReViewPoint backend. This section provides in-depth information about each component of the backend implementation.

## Overview Documents

- [Database Implementation](database-implementation.md) - Comprehensive guide to the database layer

## Core Components

- [Database Module](core/database.py.md) - SQLAlchemy async setup and session management
- [Config Module](core/config.py.md) - Application settings and configuration

## Data Models

- [Base Model](models/base.py.md) - Foundation class for all models
- [User Model](models/user.py.md) - User authentication and management
- [File Model](models/file.py.md) - Document metadata storage

## Schema Migrations

- [Alembic Configuration](alembic/env.py.md) - Database migration setup
- [Initial Migration](alembic/versions/initial_migration.md) - First migration creating core tables

## Test Infrastructure

- [Test Fixtures](tests/conftest.md) - Shared test setup and fixtures
- [Database Tests](tests/core/database_tests.md) - Tests for the database layer
- [Model Tests](tests/models/model_tests.md) - Tests for data models

## Other Resources

- [API Documentation](../api) - API endpoints and request/response schemas
- [Development Guidelines](../dev-guidelines.md) - Coding standards and practices
- [Setup Guide](../setup.md) - Getting started with development

## Documentation Template

If you're adding a new component, please use the [documentation template](_TEMPLATE.md) to maintain consistency.
