#!/usr/bin/env python3
"""Manually create migration state"""

from sqlalchemy import create_engine, text

print('Testing manual alembic setup...')
engine = create_engine('postgresql://postgres:postgres@localhost:5432/reviewpoint')

with engine.connect() as conn:
    # Create alembic version table
    conn.execute(text('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY);'))
    
    # Insert initial migration as current
    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('f140e6f46727');"))
    
    conn.commit()
    print('Alembic version table created!')
    
    # Verify
    result = conn.execute(text('SELECT version_num FROM alembic_version;'))
    current = result.fetchone()
    print(f'Current revision: {current[0] if current else None}')
