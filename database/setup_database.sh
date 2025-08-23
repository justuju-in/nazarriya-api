#!/bin/bash

echo "🚀 Setting up NazarRiya Database..."

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Find PostgreSQL tools based on OS
find_postgres_tools() {
    local os=$(detect_os)
    local paths=()
    
    case $os in
        "macos")
            paths=(
                "/Library/PostgreSQL/15/bin"
                "/Library/PostgreSQL/16/bin"
                "/Applications/PostgreSQL.app/Contents/Versions/15/bin"
                "/Applications/PostgreSQL.app/Contents/Versions/16/bin"
                "/opt/homebrew/bin"
                "/usr/local/bin"
            )
            ;;
        "linux")
            paths=(
                "/usr/bin"
                "/usr/local/bin"
                "/opt/postgresql/bin"
                "/usr/lib/postgresql/*/bin"
            )
            ;;
        "windows")
            paths=(
                "/c/Program Files/PostgreSQL/*/bin"
                "/c/Program Files (x86)/PostgreSQL/*/bin"
            )
            ;;
    esac
    
    # Check each path for PostgreSQL tools
    for path in "${paths[@]}"; do
        if [[ -d "$path" ]]; then
            # Handle wildcards in paths
            for expanded_path in $path; do
                if [[ -f "$expanded_path/psql" ]]; then
                    echo "$expanded_path"
                    return 0
                fi
            done
        fi
    done
    
    return 1
}

# Check if PostgreSQL is running
check_postgres_running() {
    local pg_isready_path="$1"
    local port="${2:-5432}"
    
    if "$pg_isready_path" -h localhost -p "$port" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Create database
create_database() {
    local createdb_path="$1"
    local db_name="$2"
    local user="${3:-postgres}"
    
    echo "📦 Creating database '$db_name'..."
    
    # Try to create database without password first
    if "$createdb_path" -h localhost -U "$user" "$db_name" 2>/dev/null; then
        echo "✅ Database '$db_name' created successfully"
        return 0
    fi
    
    # If that fails, prompt for password
    echo "🔐 Database creation requires authentication. Please enter your PostgreSQL password:"
    if "$createdb_path" -h localhost -U "$user" "$db_name"; then
        echo "✅ Database '$db_name' created successfully"
        return 0
    else
        echo "❌ Failed to create database. Please check your PostgreSQL credentials."
        return 1
    fi
}

# Main setup process
main() {
    echo "🔍 Detecting PostgreSQL installation..."
    
    # Find PostgreSQL tools
    local postgres_path=$(find_postgres_tools)
    if [[ -z "$postgres_path" ]]; then
        echo "❌ PostgreSQL command-line tools not found!"
        echo ""
        echo "Please install PostgreSQL first:"
        echo ""
        case $(detect_os) in
            "macos")
                echo "  Option 1: Download from https://www.postgresql.org/download/macosx/"
                echo "  Option 2: Install via Homebrew: brew install postgresql"
                ;;
            "linux")
                echo "  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
                echo "  CentOS/RHEL: sudo yum install postgresql postgresql-server"
                ;;
            "windows")
                echo "  Download from https://www.postgresql.org/download/windows/"
                ;;
        esac
        echo ""
        echo "After installation, ensure the PostgreSQL tools are in your PATH"
        exit 1
    fi
    
    echo "✅ Found PostgreSQL tools in: $postgres_path"
    
    # Set paths to tools
    local psql_path="$postgres_path/psql"
    local createdb_path="$postgres_path/createdb"
    local pg_isready_path="$postgres_path/pg_isready"
    
    # Check if PostgreSQL is running
    echo "🔍 Checking if PostgreSQL is running..."
    if ! check_postgres_running "$pg_isready_path" 5432; then
        echo "❌ PostgreSQL is not running on port 5432"
        echo ""
        echo "Please start PostgreSQL:"
        case $(detect_os) in
            "macos")
                echo "  - Through pgAdmin4 application"
                echo "  - Or via Homebrew: brew services start postgresql"
                ;;
            "linux")
                echo "  - sudo systemctl start postgresql"
                echo "  - Or sudo service postgresql start"
                ;;
            "windows")
                echo "  - Through Windows Services"
                echo "  - Or start the PostgreSQL service manually"
                ;;
        esac
        exit 1
    fi
    
    echo "✅ PostgreSQL is running on port 5432"
    
    # Create database
    if ! create_database "$createdb_path" "nazarriya"; then
        exit 1
    fi
    
    # Install Python dependencies
    echo "📚 Installing Python dependencies..."
    if ! pip install -r requirements.txt; then
        echo "❌ Failed to install Python dependencies"
        echo "You may need to upgrade pip: pip install --upgrade pip"
        exit 1
    fi
    
    # Initialize Alembic
    echo "🔧 Initializing Alembic..."
    if [[ ! -d "alembic" ]]; then
        alembic init alembic
    else
        echo "Alembic already initialized"
    fi
    
    # Update alembic.ini with correct database URL
    echo "🔧 Updating Alembic configuration..."
    local os=$(detect_os)
    local db_url=""
    
    case $os in
        "windows")
            # Windows uses different sed syntax
            sed -i "s|sqlalchemy.url = .*|sqlalchemy.url = postgresql://postgres@localhost:5432/nazarriya|" alembic.ini
            ;;
        *)
            sed -i '' "s|sqlalchemy.url = .*|sqlalchemy.url = postgresql://postgres@localhost:5432/nazarriya|" alembic.ini
            ;;
    esac
    
    # Create initial migration
    echo "📝 Creating initial migration..."
    if ! alembic revision --autogenerate -m "Initial migration"; then
        echo "❌ Failed to create migration. Please check your models and database connection."
        exit 1
    fi
    
    # Run migrations
    echo "🚀 Running database migrations..."
    if ! alembic upgrade head; then
        echo "❌ Failed to run migrations. Please check the error messages above."
        exit 1
    fi
    
    # Initialize database with sample data
    echo "🎯 Initializing database with sample data..."
    cd server
    if ! python init_db.py; then
        echo "❌ Failed to initialize sample data. Please check the error messages above."
        exit 1
    fi
    cd ..
    
    echo "✅ Database setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update your environment variables in .env file"
    echo "2. Start implementing JWT authentication"
    echo "3. Update the chat router to use the database"
    echo ""
    echo "🌐 You can now start your server with:"
    echo "   cd server && uvicorn main:app --reload"
}

# Run main function
main "$@"
