#!/usr/bin/env python3
"""
Script to wait for database to be ready before running migrations
"""
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db(database_url, max_attempts=30):
    """Wait for database to be ready"""
    print("Waiting for database to be ready...")
    
    for attempt in range(max_attempts):
        try:
            # Parse the database URL
            parsed = urlparse(database_url)
            
            # Try to connect
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],  # Remove leading slash
                user=parsed.username,
                password=parsed.password
            )
            
            # Test the connection
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.fetchone()
            cur.close()
            conn.close()
            
            print("Database is ready!")
            return True
            
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"Database not ready yet (attempt {attempt + 1}/{max_attempts}): {e}")
                time.sleep(2)
            else:
                print(f"Failed to connect to database after {max_attempts} attempts")
                return False
    
    return False

if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    if wait_for_db(database_url):
        sys.exit(0)
    else:
        sys.exit(1)
