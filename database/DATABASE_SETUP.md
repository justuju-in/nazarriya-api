# Database Setup Guide for NazarRiya Backend

## Prerequisites

1. **PostgreSQL** installed and running
2. **Python 3.8+** with pip
3. **Git** (to clone the repository)

## Quick Setup

### 1. Install PostgreSQL

**On macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**On Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

### 2. Create Database User (Optional but Recommended)

```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create a new user and database
CREATE USER nazarriya_user WITH PASSWORD 'your_password';
CREATE DATABASE nazarriya OWNER nazarriya_user;
GRANT ALL PRIVILEGES ON DATABASE nazarriya TO nazarriya_user;
\q
```

### 3. Run the Setup Script

**Cross-platform Python script (Recommended):**
```bash
python setup_database.py
```

**On macOS/Linux:**
```bash
# Make the script executable
chmod +x setup_database.sh

# Run the setup script
./setup_database.sh
```

**On Windows:**
```cmd
setup_database.bat
```

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Database
```bash
createdb -h localhost -U postgres nazarriya
```

### 3. Set Environment Variables
```bash
cp env.example .env
# Edit .env with your database credentials
```

### 4. Run Migrations
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Initialize Sample Data
```bash
cd server
python init_db.py
```

## Database Schema

The database includes the following tables:

### Users Table
- **id**: UUID primary key
- **email**: Unique email address
- **hashed_password**: Encrypted password
- **first_name**: User's first name
- **age**: User's age
- **preferred_language**: Preferred language (English/Hindi)
- **state**: Indian state
- **is_active**: Account status
- **created_at**: Account creation timestamp
- **updated_at**: Last update timestamp

### Chat Sessions Table
- **id**: UUID primary key
- **user_id**: Foreign key to users table
- **title**: Session title (auto-generated)
- **metadata**: JSON field for session context
- **created_at**: Session creation timestamp
- **updated_at**: Last activity timestamp

### Chat Messages Table
- **id**: UUID primary key
- **session_id**: Foreign key to chat_sessions table
- **sender_type**: 'user' or 'bot'
- **content**: Message content
- **metadata**: JSON field for sources, context
- **created_at**: Message timestamp

## Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/nazarriya

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Configuration
DEBUG=True
APP_NAME=NazarRiya Backend
```

## Troubleshooting

### Common Issues

1. **PostgreSQL Connection Error**
   - Ensure PostgreSQL is running
   - Check if the port 5432 is available
   - Verify database credentials

2. **Permission Denied**
   - Check if the database user has proper permissions
   - Ensure the database exists

3. **Migration Errors**
   - Check if all models are properly imported
   - Verify database connection string

4. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path and working directory

### Useful Commands

```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Connect to database
psql -h localhost -U postgres -d nazarriya

# List all tables
\dt

# Check table structure
\d+ table_name

# Reset database (WARNING: This will delete all data)
dropdb -h localhost -U postgres nazarriya
createdb -h localhost -U postgres nazarriya
alembic upgrade head
```

## Next Steps

After successful database setup:

1. **Implement JWT Authentication** in `server/auth/`
2. **Update Chat Router** to use database instead of in-memory storage
3. **Add User Management Endpoints** (register, login, profile)
4. **Implement Session Management** with proper user isolation
5. **Add Data Validation** and error handling

## Production Considerations

1. **Use Environment Variables** for all sensitive data
2. **Implement Connection Pooling** for better performance
3. **Set up Database Backups** and monitoring
4. **Use SSL Connections** for cloud deployments
5. **Implement Rate Limiting** and security measures
