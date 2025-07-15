#!/usr/bin/env python3
"""Test Alembic migration step by step"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

# Load environment
from dotenv import load_dotenv
load_dotenv(backend_dir / "config" / ".env")

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

try:
    print("=== ALEMBIC DEBUG SESSION ===")
    
    # Set up config
    alembic_cfg = Config(str(backend_dir / "alembic.ini"))
    
    # Test script directory
    print("Testing script directory...")
    script_dir = ScriptDirectory.from_config(alembic_cfg)
    revisions = list(script_dir.walk_revisions())
    print(f"Found {len(revisions)} revisions:")
    for rev in revisions:
        print(f"  - {rev.revision}: {rev.doc}")
    
    # Test database connection
    db_url = os.getenv('REVIEWPOINT_DB_URL', 'postgresql://postgres:postgres@localhost:5432/reviewpoint')
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"Database URL: {sync_url}")
    
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        print("Database connection successful")
        
        # Test if alembic_version table exists
        from sqlalchemy import text
        try:
            result = conn.execute(text("SELECT version_num FROM alembic_version;"))
            current = result.fetchone()
            print(f"Current alembic version: {current[0] if current else 'None'}")
        except Exception as e:
            print(f"No alembic_version table: {e}")
    
    # Try upgrading one step at a time
    print("\n=== ATTEMPTING UPGRADE ===")
    
    # First create the alembic version table
    print("Stamping base...")
    command.stamp(alembic_cfg, "base")
    
    print("Getting current revision...")
    from alembic.runtime.migration import MigrationContext
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        current = context.get_current_revision()
        print(f"Current revision after stamp: {current}")
    
    print("Upgrading to head...")
    command.upgrade(alembic_cfg, "head")
    
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        current = context.get_current_revision()
        print(f"Current revision after upgrade: {current}")
        
        # Check what tables exist now
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables after migration: {tables}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
