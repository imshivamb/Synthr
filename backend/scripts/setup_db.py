import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from alembic import command
from alembic.config import Config

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

def create_database():
    """Create the database if it doesn't exist"""
    db_params = {
        "host": os.getenv("POSTGRES_SERVER", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5436"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "dbname": "postgres"  # Connect to default postgres database first
    }

    target_db = os.getenv("POSTGRES_DB", "synthr_db")

    try:
        print(f"Connecting to PostgreSQL on port {db_params['port']}...")
        # Connect to default postgres database
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cur = conn.cursor()

        # Check if database exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{target_db}'")
        exists = cur.fetchone()
        
        if not exists:
            # Create database
            cur.execute(f'CREATE DATABASE "{target_db}"')
            print(f"✅ Database {target_db} created successfully!")
        else:
            print(f"ℹ️ Database {target_db} already exists.")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("Current connection parameters:")
        print(f"  Host: {db_params['host']}")
        print(f"  Port: {db_params['port']}")
        print(f"  User: {db_params['user']}")
        print(f"  Database: {db_params['dbname']}")
        return False

def create_initial_migration():
    """Create and run initial database migration"""
    try:
        # Get the directory of the current file
        current_dir = Path(__file__).parent.parent

        # Create alembic.ini
        alembic_cfg = Config(str(current_dir / "alembic.ini"))
        
        # Set the SQLAlchemy URL in the config
        db_url = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'postgres')}@{os.getenv('POSTGRES_SERVER', 'localhost')}:{os.getenv('POSTGRES_PORT', '5436')}/{os.getenv('POSTGRES_DB', 'synthr_db')}"
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        # Create initial migration
        command.revision(
            alembic_cfg,
            message="initial_migration",
            autogenerate=True
        )
        print("✅ Initial migration created successfully!")

        # Apply migration
        command.upgrade(alembic_cfg, "head")
        print("✅ Migration applied successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with migrations: {e}")
        return False

def setup_database():
    """Complete database setup process"""
    print("\n🚀 Starting database setup...\n")

    if create_database():
        print("\n📦 Creating and applying migrations...\n")
        if create_initial_migration():
            print("\n✨ Database setup completed successfully!")
        else:
            print("\n❌ Failed to create migrations.")
    else:
        print("\n❌ Failed to create database.")

if __name__ == "__main__":
    setup_database()