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

The database includes the following tables with their complete DDL statements:

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    age INTEGER,
    preferred_language VARCHAR(50),
    state VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create index on email for faster lookups
CREATE INDEX ix_users_email ON users (email);
```

**Table Description:**
- **id**: UUID primary key, auto-generated
- **email**: Unique email address (indexed)
- **hashed_password**: Encrypted password hash
- **first_name**: User's first name (optional)
- **age**: User's age (optional)
- **preferred_language**: Preferred language - English/Hindi (optional)
- **state**: Indian state (optional)
- **is_active**: Account status, defaults to TRUE
- **created_at**: Account creation timestamp, auto-set
- **updated_at**: Last update timestamp, auto-updated

### Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    session_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create index on user_id for faster user session lookups
CREATE INDEX ix_chat_sessions_user_id ON chat_sessions (user_id);
```

**Table Description:**
- **id**: UUID primary key, auto-generated
- **user_id**: Foreign key to users table (cascade delete)
- **title**: Session title, auto-generated from first message (optional)
- **session_data**: JSONB field for session context and preferences
- **created_at**: Session creation timestamp, auto-set
- **updated_at**: Last activity timestamp, auto-updated

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on session_id for faster message retrieval
CREATE INDEX ix_chat_messages_session_id ON chat_messages (session_id);
```

**Table Description:**
- **id**: UUID primary key, auto-generated
- **session_id**: Foreign key to chat_sessions table (cascade delete)
- **sender_type**: Message sender - 'user' or 'bot'
- **content**: Message text content
- **message_data**: JSONB field for sources, context, and metadata
- **created_at**: Message timestamp, auto-set

### Complete Database Creation Script
```sql
-- Create all tables in the correct order (respecting foreign key dependencies)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    age INTEGER,
    preferred_language VARCHAR(50),
    state VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_users_email ON users (email);

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    session_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_chat_sessions_user_id ON chat_sessions (user_id);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_chat_messages_session_id ON chat_messages (session_id);
```

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
