#!/usr/bin/env python3
"""Check for indexes related to used_password_reset_tokens."""

import psycopg2

def main():
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/reviewpoint')
    cursor = conn.cursor()
    
    # Check for indexes containing 'used_password_reset_tokens'
    cursor.execute("""
        SELECT schemaname, tablename, indexname 
        FROM pg_indexes 
        WHERE indexname LIKE '%used_password_reset_tokens%';
    """)
    
    print("Indexes containing 'used_password_reset_tokens':")
    for row in cursor.fetchall():
        print(f'  Schema: {row[0]}, Table: {row[1]}, Index: {row[2]}')
    
    # Check for the specific table
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'used_password_reset_tokens'
        );
    """)
    table_exists = cursor.fetchone()[0]
    print(f'used_password_reset_tokens table exists: {table_exists}')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
