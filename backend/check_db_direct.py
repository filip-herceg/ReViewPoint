#!/usr/bin/env python3
"""Direct PostgreSQL database check without going through app config."""

import psycopg2

def main():
    # Direct connection using sync URL
    sync_url = "postgresql://postgres:postgres@localhost:5432/reviewpoint"
    print(f'Connecting to: {sync_url}')

    try:
        conn = psycopg2.connect(sync_url)
        cursor = conn.cursor()
        
        # Check if alembic_version table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'alembic_version'
            );
        """)
        result = cursor.fetchone()
        alembic_exists = result[0] if result else False
        print(f'Alembic version table exists: {alembic_exists}')
        
        if alembic_exists:
            cursor.execute('SELECT version_num FROM alembic_version;')
            version_result = cursor.fetchone()
            print(f'Current alembic version: {version_result[0] if version_result else "None"}')
        
        # List all tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f'All tables: {[t[0] for t in tables]}')
        
        # List all indexes
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE schemaname = 'public' 
            ORDER BY indexname;
        """)
        indexes = cursor.fetchall()
        print(f'All indexes: {[i[0] for i in indexes]}')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()
