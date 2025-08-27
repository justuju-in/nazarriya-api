#!/usr/bin/env python3
"""
Cross-platform database setup script for NazarRiya Backend
Works on macOS, Linux, and Windows
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_status(message, status="ℹ️"):
    """Print a formatted status message"""
    print(f"{status} {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def detect_os():
    """Detect the operating system"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"

def find_postgres_tools():
    """Find PostgreSQL tools based on OS"""
    os_type = detect_os()
    search_paths = []
    
    if os_type == "macos":
        search_paths = [
            "/Library/PostgreSQL/15/bin",
            "/Library/PostgreSQL/16/bin",
            "/Applications/PostgreSQL.app/Contents/Versions/15/bin",
            "/Applications/PostgreSQL.app/Contents/Versions/16/bin",
            "/opt/homebrew/bin",
            "/usr/local/bin"
        ]
    elif os_type == "linux":
        search_paths = [
            "/usr/bin",
            "/usr/local/bin",
            "/opt/postgresql/bin"
        ]
        # Add wildcard paths for Linux
        for version in ["15", "16", "14", "13"]:
            search_paths.append(f"/usr/lib/postgresql/{version}/bin")
    elif os_type == "windows":
        search_paths = [
            "C:\\Program Files\\PostgreSQL\\15\\bin",
            "C:\\Program Files\\PostgreSQL\\16\\bin",
            "C:\\Program Files (x86)\\PostgreSQL\\15\\bin",
            "C:\\Program Files (x86)\\PostgreSQL\\16\\bin"
        ]
    
    # Check each path for PostgreSQL tools
    for path in search_paths:
        if os.path.isdir(path):
            psql_path = os.path.join(path, "psql.exe" if os_type == "windows" else "psql")
            if os.path.isfile(psql_path):
                return path
    
    return None

def check_postgres_running(pg_isready_path):
    """Check if PostgreSQL is running"""
    try:
        result = subprocess.run(
            [pg_isready_path, "-h", "localhost", "-p", "5432"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def check_database_exists(psql_path, db_name, user="postgres"):
    """Check if database already exists"""
    try:
        result = subprocess.run(
            [psql_path, "-h", "localhost", "-U", user, "-lqt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Check if our database name appears in the list
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and db_name in line:
                    return True
        return False
    except Exception:
        return False

def check_database_has_tables(psql_path, db_name, user="postgres"):
    """Check if database has tables"""
    try:
        result = subprocess.run(
            [psql_path, "-h", "localhost", "-U", user, "-d", db_name, "-c", "\\dt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Check if there are any tables (output should contain table names)
            lines = result.stdout.strip().split('\n')
            # Skip header lines and look for actual table entries
            for line in lines:
                if line.strip() and not line.startswith('---') and '|' in line:
                    return True
        return False
    except Exception:
        return False

def create_database(createdb_path, db_name, user="postgres"):
    """Create a new database"""
    try:
        result = subprocess.run(
            [createdb_path, "-h", "localhost", "-U", user, db_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success(f"Database '{db_name}' created successfully")
            return True
        else:
            print_error(f"Failed to create database: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Error creating database: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print_status("Installing Python dependencies...")
    
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        requirements_file = os.path.join(script_dir, "..", "requirements.txt")
        
        # Check if requirements.txt exists
        if not os.path.exists(requirements_file):
            print_error("requirements.txt not found in parent directory")
            return False
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Dependencies installed successfully")
            return True
        else:
            print_error(f"Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Error installing dependencies: {e}")
        return False

def init_alembic():
    """Initialize Alembic"""
    print_status("Initializing Alembic...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(os.path.join(script_dir, "alembic")):
        try:
            result = subprocess.run(
                ["alembic", "init", "alembic"],
                capture_output=True,
                text=True,
                cwd=script_dir
            )
            
            if result.returncode != 0:
                print_error("Failed to initialize Alembic")
                return False
        except Exception as e:
            print_error(f"Error initializing Alembic: {e}")
            return False
        

    else:
        print_status("Alembic already initialized")
    
    # Ensure the versions directory exists
    versions_dir = os.path.join(script_dir, "alembic", "versions")
    if not os.path.exists(versions_dir):
        os.makedirs(versions_dir)
        print_status("Created alembic/versions directory")
    
    return True



def update_alembic_config():
    """Update alembic.ini with correct database URL"""
    print_status("Updating Alembic configuration...")
    
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alembic_ini = Path(os.path.join(script_dir, "alembic.ini"))
        if alembic_ini.exists():
            content = alembic_ini.read_text()
            content = content.replace(
                "sqlalchemy.url = driver://user:pass@localhost/dbname",
                "sqlalchemy.url = postgresql://postgres@localhost:5432/nazarriya"
            )
            alembic_ini.write_text(content)
            print_success("Alembic configuration updated")
        return True
    except Exception as e:
        print_error(f"Error updating Alembic configuration: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    # Get the database directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set PYTHONPATH to include both the server directory and the parent directory
    env = os.environ.copy()
    server_dir = os.path.join(script_dir, "..", "server")
    parent_dir = os.path.dirname(script_dir)
    env['PYTHONPATH'] = f"{server_dir}:{parent_dir}"
    
    # Check if there are existing migrations
    versions_dir = os.path.join(script_dir, "alembic", "versions")
    existing_migrations = [f for f in os.listdir(versions_dir) if f.endswith('.py') and not f.startswith('__')]
    
    if existing_migrations:
        print_status(f"Found existing migrations: {', '.join(existing_migrations)}")
        print_status("Using existing migrations instead of creating new ones...")
    else:
        print_status("Creating initial migration...")
        
        try:
            result = subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
                capture_output=True,
                text=True,
                env=env,
                cwd=script_dir  # Run from database directory where alembic.ini is located
            )
            
            if result.returncode != 0:
                print_error("Failed to create migration. Please check your models and database connection.")
                print_error(f"Error details: {result.stderr}")
                print_error(f"Command output: {result.stdout}")
                return False
            else:
                print_success("Initial migration created successfully")
        except Exception as e:
            print_error(f"Error creating migration: {e}")
            return False
    
    print_status("Running database migrations...")
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            env=env,
            cwd=script_dir  # Run from database directory where alembic.ini is located
        )
        
        if result.returncode != 0:
            print_error("Failed to run migrations. Please check the error messages above.")
            return False
    except Exception as e:
        print_error(f"Error running migrations: {e}")
        return False
    
    return True

def test_database_connection(psql_path, db_name, user="postgres"):
    """Test connection to the database"""
    try:
        result = subprocess.run(
            [psql_path, "-h", "localhost", "-U", user, "-d", db_name, "-c", "SELECT 1"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def init_sample_data():
    """Initialize database with sample data"""
    print_status("Initializing database with sample data...")
    
    try:
        # Get the server directory path (relative to the database directory)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        # Set PYTHONPATH to include the parent directory so server can be imported as a module
        env = os.environ.copy()
        env['PYTHONPATH'] = parent_dir
        
        # Run init_db.py as a module to avoid relative import issues
        result = subprocess.run(
            [sys.executable, "-m", "server.init_db"],
            capture_output=True,
            text=True,
            env=env,
            cwd=parent_dir
        )
        
        if result.returncode != 0:
            print_error("Failed to initialize sample data. Please check the error messages above.")
            print_error(f"Error details: {result.stderr}")
            print_error(f"Command output: {result.stdout}")
            return False
            
        print_success("Sample data initialized successfully")
        return True
        
    except Exception as e:
        print_error(f"Error initializing sample data: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 Setting up NazarRiya Database...")
    
    # Check for database credentials
    if not os.getenv("POSTGRES_PASSWORD") and not os.getenv("DATABASE_URL"):
        print_status("🔑 No database credentials found in environment variables")
        print_status("   You may need to set POSTGRES_PASSWORD or DATABASE_URL")
        print_status("   Common default password: 'postgres' (try: export POSTGRES_PASSWORD=postgres)")
        print_status("")
    
    # Detect OS
    os_type = detect_os()
    print_status(f"Detected OS: {os_type}")
    
    # Find PostgreSQL tools
    print_status("Detecting PostgreSQL installation...")
    postgres_path = find_postgres_tools()
    
    if not postgres_path:
        print_error("PostgreSQL command-line tools not found!")
        print()
        print("Please install PostgreSQL first:")
        print()
        
        if os_type == "macos":
            print("  Option 1: Download from https://www.postgresql.org/download/macosx/")
            print("  Option 2: Install via Homebrew: brew install postgresql")
        elif os_type == "linux":
            print("  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib")
            print("  CentOS/RHEL: sudo yum install postgresql postgresql-server")
        elif os_type == "windows":
            print("  Download from https://www.postgresql.org/download/windows/")
        
        print()
        print("After installation, ensure the PostgreSQL tools are in your PATH")
        return False
    
    print_success(f"Found PostgreSQL tools in: {postgres_path}")
    
    # Set paths to tools
    psql_path = os.path.join(postgres_path, "psql.exe" if os_type == "windows" else "psql")
    createdb_path = os.path.join(postgres_path, "createdb.exe" if os_type == "windows" else "createdb")
    pg_isready_path = os.path.join(postgres_path, "pg_isready.exe" if os_type == "windows" else "pg_isready")
    
    # Check if PostgreSQL is running
    print_status("Checking if PostgreSQL is running...")
    if not check_postgres_running(pg_isready_path):
        print_error("PostgreSQL is not running on port 5432")
        print()
        print("Please start PostgreSQL:")
        
        if os_type == "macos":
            print("  - Through pgAdmin4 application")
            print("  - Or via Homebrew: brew services start postgresql")
        elif os_type == "linux":
            print("  - sudo systemctl start postgresql")
            print("  - Or sudo service postgresql start")
        elif os_type == "windows":
            print("  - Through Windows Services")
            print("  - Or start the PostgreSQL service manually")
        
        return False
    
    print_success("PostgreSQL is running on port 5432")
    
    # Check if database already exists
    if check_database_exists(psql_path, "nazarriya"):
        print_success("Database 'nazarriya' already exists")
        
        # Check if it already has our tables
        if check_database_has_tables(psql_path, "nazarriya"):
            print_success("Database already has tables - setup appears complete!")
            print()
            print("🌐 You can start your server with:")
            print("   cd server && uvicorn main:app --reload")
            print("   (from the nazarriya-api directory)")
            return True
    else:
        # Create database if it doesn't exist
        if not create_database(createdb_path, "nazarriya"):
            return False
    
    # Install Python dependencies FIRST (needed for Alembic)
    if not install_dependencies():
        return False
    
    # Initialize Alembic
    if not init_alembic():
        return False
    
    # Update Alembic configuration
    if not update_alembic_config():
        return False
    
    # Test database connection before migrations
    print_status("Testing database connection...")
    if not test_database_connection(psql_path, "nazarriya"):
        print_error("Cannot connect to database 'nazarriya'. Please check your credentials.")
        print_error("")
        print_error("🔑 Authentication Options:")
        print_error("1. Set POSTGRES_PASSWORD environment variable:")
        print_error("   export POSTGRES_PASSWORD='your_postgres_password'")
        print_error("2. Set DATABASE_URL environment variable:")
        print_error("   export DATABASE_URL='postgresql://postgres:your_password@localhost:5432/nazarriya'")
        print_error("3. Create .pgpass file in your home directory")
        print_error("")
        print_error("Common default passwords: 'postgres', 'admin', 'password', or empty string")
        return False
    
    print_success("Database connection successful")
    
    # Run migrations
    if not run_migrations():
        return False
    
    # Initialize sample data
    if not init_sample_data():
        return False
    
    print_success("Database setup complete!")
    print()
    print("🌐 You can now start your server with:")
    print("   cd server && uvicorn main:app --reload")
    print("   (from the nazarriya-api directory)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
