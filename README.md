# nazarriya-api
NazarRiya web server

- [Developer instructions](#developer-instructions)
  * [Cloud deployment](#cloud-deployment)
  * [Local deployment](#local-deployment)
    + [Setting up the entire backend: API + LLM servers + DBs](#setting-up-the-entire-backend--api---llm-servers---dbs)
      - [0. Setup](#0-setup)
      - [1. Environment Variables](#1-environment-variables)
      - [3. Run Docker Compose](#3-run-docker-compose)
      - [4. Test both the servers](#4-test-both-the-servers)
    + [Setting up only the API server](#setting-up-only-the-api-server)
      - [1. Environment Variables](#1-environment-variables-1)
      - [2. Setup DB](#2-setup-db)
      - [3. Run server](#3-run-server)
      - [4. Test](#4-test)
- [API Usage Examples](#api-usage-examples)
  * [User Registration](#user-registration)
  * [User Login](#user-login)
  * [Get Current User Profile](#get-current-user-profile)
  * [Create a New Chat Session](#create-a-new-chat-session)
  * [Send a Chat Message](#send-a-chat-message)
  * [Get User Sessions](#get-user-sessions)
  * [Get Session History](#get-session-history)
  * [Update Session Title](#update-session-title)
  * [Delete Session](#delete-session)
- [🏗️ Architecture](#----architecture)
  * [File Structure](#file-structure)
  * [Authentication Flow](#authentication-flow)
  * [Security Implementation](#security-implementation)
- [🔧 Configuration](#---configuration)
  * [JWT Settings](#jwt-settings)
  * [Database Integration](#database-integration)
  * [Production Checklist](#production-checklist)
  * [Best Practices](#best-practices)
  * [Debug Mode](#debug-mode)

# Developer instructions

Clone repo: `git clone git@github.com:paulrahul/nazarriya-api.git`

## Cloud deployment
Check DEPLOYMENT.md

## Local deployment

### Setting up the entire backend: API + LLM servers + DBs

#### 0. Setup
Clone LLM repo too: `git clone git@github.com:justuju-in/nazarriya-llm.git`
Install Docker Compose: https://docs.docker.com/compose/install/

#### 1. Environment Variables
Set the following environment variables in your system:

```bash
# master_env.sh
export OPENAI_API_KEY="your_key_here"
export OPENAI_MODEL="gpt-3.5-turbo"
export OPENAI_EMBEDDING_MODEL="text-embedding-ada-002"

# Database Configuration
export POSTGRES_PASSWORD="your_secure_password_here"

# API Server Configuration
# You can use python3 -c "import secrets; print(secrets.token_urlsafe(32))" to generate a 32-byte random key.
export SECRET_KEY="your_very_long_random_secret_key_here"
export ACCESS_TOKEN_EXPIRE_MINUTES="1440"
export DEBUG="False"

# LLM Service Configuration
export CHUNK_SIZE="1000"
export CHUNK_OVERLAP="200"
export MAX_TOKENS="1000"
```

**Note**: Never commit environment variables to version control. Each developer should set these in their local environment.

#### 3. Run Docker Compose 
This will setup all the servers and DBs and install all dependencies.

```bash
cd nazarriya-api
docker-compose up -d
```

#### 4. Test both the servers
```bash
# Test the LLM server
cd ../nazarriya-llm
python test_service.py

# Test the complete API server
cd ../nazarriya-api
python test/run_tests.py
```

### Setting up only the API server
Install dependencies: `pip install -r requirements.txt`
Install PostgreSQL: https://www.postgresql.org/download/

#### 1. Environment Variables
Set the following environment variables in your system:

```bash
# Database
export DATABASE_URL="postgresql://postgres:password@localhost:5432/nazarriya"

# JWT Security (CHANGE THIS IN PRODUCTION!)
export SECRET_KEY="your-super-secret-key-change-this-in-production"
export ACCESS_TOKEN_EXPIRE_MINUTES="30"

# App Settings
export DEBUG="False"
export HOST="0.0.0.0"
export PORT="8000"
```

**Note**: Never commit environment variables to version control. Each developer should set these in their local environment.

#### 2. Setup DB
```bash
# Run *.bat for Windows or .sh for Linux but if you have Python, then running the .py script is the best option.
python database/setup_database.py
```

#### 3. Run server
```bash
uvicorn server.main:app --reload
```

#### 4. Test
```bash
# Test the complete authentication system
python test/run_tests.py
```

# API Usage Examples

## User Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "age": 30,
    "preferred_language": "English",
    "state": "California"
  }'
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "first_name": "John",
  "age": 30,
  "preferred_language": "English",
  "state": "California",
  "created_at": "2024-01-01T00:00:00"
}
```

## User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "first_name": "John",
    "age": 30,
    "preferred_language": "English",
    "state": "California",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## Get Current User Profile
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## Create a New Chat Session
```bash
curl -X POST "http://localhost:8000/chat/sessions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My New Chat"}'
```

## Send a Chat Message
```bash
curl -X POST "http://localhost:8000/chat/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "session_id": "SESSION_UUID"}'
```

## Get User Sessions
```bash
curl -X GET "http://localhost:8000/chat/sessions?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Get Session History
```bash
curl -X GET "http://localhost:8000/chat/sessions/SESSION_UUID/history" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Update Session Title
```bash
curl -X PUT "http://localhost:8000/chat/sessions/SESSION_UUID/title" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

## Delete Session
```bash
curl -X DELETE "http://localhost:8000/chat/sessions/SESSION_UUID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

# 🏗️ Architecture

## File Structure
```
server/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy models and Pydantic schemas
├── dependencies.py      # Authentication dependencies
├── utils/
│   └── auth.py         # JWT and password utilities
├── routers/
│   ├── auth.py         # Authentication endpoints
│   └── chat.py         # Protected chat endpoints
└── session_manager.py   # Chat session management
```

## Authentication Flow
1. **Registration**: User creates account → Password hashed → User stored in DB
2. **Login**: User provides credentials → Password verified → JWT token generated
3. **Protected Access**: Token included in request → Token validated → User authenticated
4. **Session Management**: User ID extracted from token → Chat sessions created/accessed

## Security Implementation
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: HS256 algorithm, configurable expiration
- **Route Protection**: Dependency injection for authentication
- **Database Sessions**: Secure session management with PostgreSQL

# 🔧 Configuration

## JWT Settings
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 30 minutes (configurable)
- **Secret Key**: Environment variable (change in production)

## Database Integration
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Connection Pooling**: Enabled with health checks
- **Migrations**: Alembic support

## Production Checklist
- [ ] Change `SECRET_KEY` environment variable to strong random value
- [ ] Set `DEBUG=False` environment variable
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Add comprehensive logging
- [ ] Regular security audits

## Best Practices
- Tokens expire automatically
- Passwords are never stored in plain text
- User sessions are isolated
- Database connections are pooled and secured

## Debug Mode
Set `export DEBUG="True"` in your environment for detailed error messages and auto-reload.
