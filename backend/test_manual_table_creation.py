#!/usr/bin/env python3
"""Manual execution of the initial migration to see what happens"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

from sqlalchemy import create_engine, MetaData
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

# Import our models to get the metadata
from models import Base

# Connect to database
engine = create_engine("postgresql://postgres:postgres@localhost:5432/reviewpoint")

print("=== MANUAL MIGRATION TEST ===")

with engine.connect() as conn:
    print("Connected to database")
    
    # Set up migration context
    context = MigrationContext.configure(conn)
    op = Operations(context)
    
    print("Creating tables using SQLAlchemy MetaData...")
    
    try:
        # Try creating all tables from our models
        Base.metadata.create_all(engine)
        print("Tables created successfully using Base.metadata.create_all()")
        
        # Check what was created
        from sqlalchemy import text
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables in database: {tables}")
        
        if tables:
            print("SUCCESS! Tables were created!")
            for table in tables:
                # Get column info for each table
                result = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position;"))
                columns = [(row[0], row[1]) for row in result.fetchall()]
                print(f"  {table}: {len(columns)} columns")
                for col_name, col_type in columns[:3]:  # Show first 3 columns
                    print(f"    - {col_name}: {col_type}")
                if len(columns) > 3:
                    print(f"    ... and {len(columns) - 3} more columns")
        else:
            print("No tables were created.")
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
