import psycopg2
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

def check_db_connection():
    """Check if we can connect to the database"""
    db_params = {
        "host": os.getenv("POSTGRES_SERVER", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5433"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "dbname": os.getenv("POSTGRES_DB", "synthr_db")
    }

    max_retries = 5
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1} of {max_retries} to connect to database...")
            conn = psycopg2.connect(**db_params)
            
            # Get database info
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            
            print("\n✅ Successfully connected to the database!")
            print(f"📋 Database Info:")
            print(f"   - Host: {db_params['host']}")
            print(f"   - Port: {db_params['port']}")
            print(f"   - Database: {db_params['dbname']}")
            print(f"   - Version: {version[0]}")
            
            cur.close()
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Connection failed: {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("\n❌ Failed to connect to the database after multiple attempts")
                print(f"Error: {e}")
                return False

if __name__ == "__main__":
    print("\n🔍 Checking database connection...")
    check_db_connection()