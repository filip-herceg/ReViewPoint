#!/usr/bin/env python3
"""Check the alembic_version table structure."""

import psycopg2

def main():
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/reviewpoint')
    cursor = conn.cursor()
    
    # Check the table structure
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'alembic_version' AND table_schema = 'public';
    """)
    
    print("alembic_version table structure:")
    for row in cursor.fetchall():
        print(f'  Column: {row[0]}, Type: {row[1]}, Max Length: {row[2]}')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
