#!/usr/bin/env python3
"""Test direct database migration"""

from sqlalchemy import create_engine, text

# Connect to database
engine = create_engine("postgresql://postgres:postgres@localhost:5432/reviewpoint")

print("Testing database connection...")
with engine.connect() as conn:
    result = conn.execute(text("SELECT current_database(), current_user;"))
    row = result.fetchone()
    print(f"Connected to database: {row[0]} as user: {row[1]}")
    
    print("Creating a test table...")
    conn.execute(text("CREATE TABLE IF NOT EXISTS test_migration (id SERIAL PRIMARY KEY, name TEXT);"))
    
    print("Checking if table exists...")
    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"))
    tables = [row[0] for row in result.fetchall()]
    print(f"Tables in database: {tables}")
    
    print("Dropping test table...")
    conn.execute(text("DROP TABLE IF EXISTS test_migration;"))
    
    conn.commit()
    print("Direct database operations successful!")
