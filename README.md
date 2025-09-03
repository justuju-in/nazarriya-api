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
      - [5. Redeployment after changes](#5-redeployment-after-changes)
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
- [🏗️ Architecture](#architecture)
  * [File Structure](#file-structure)
  * [Authentication Flow](#authentication-flow)
  * [Security Implementation](#security-implementation)
- [🔧 Configuration](#configuration)
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

#### 5. Redeployment after changes
a. First make sure you sync both backend repos to the latest code
```
cd ../nazarriya-llm
git pull --rebase

cd ../nazarriya-api
git pull --rebase
```
b. Then bring down current Docker containers, rebuild and respawn
```bash
docker-compose down
docker-compose up -d --build
```
c. Run the tests in step #4 again.

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
    "phone_number": "+1234567890",
    "first_name": "John",
    "age": 30,
    "gender": "M",
    "preferred_language": "English",
    "state": "California",
    "preferred_bot": "N"
  }'
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "phone_number": "+1234567890",
  "first_name": "John",
  "age": 30,
  "gender": "M",
  "preferred_language": "English",
  "state": "California",
  "preferred_bot": "N",
  "created_at": "2024-01-01T00:00:00"
}
```

## User Login
Login supports both email and phone number:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "user@example.com",
    "password": "securepassword123"
  }'
```

Or login with phone number:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "+1234567890",
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
    "phone_number": "+1234567890",
    "first_name": "John",
    "age": 30,
    "gender": "M",
    "preferred_language": "English",
    "state": "California",
    "preferred_bot": "N",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## Get Current User Profile
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## Update User Profile
```bash
curl -X PUT "http://localhost:8000/auth/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John Updated",
    "age": 31,
    "preferred_language": "Spanish",
    "state": "New York"
  }'
```

## Create a New Chat Session
```bash
curl -X POST "http://localhost:8000/api/sessions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My New Chat"}'
```

## Send an Encrypted Chat Message
**Note**: All chat messages are end-to-end encrypted. The client must encrypt the message before sending.

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "encrypted_message": "base64_encoded_encrypted_message",
    "encryption_metadata": {
      "algorithm": "AES-GCM",
      "key_id": "user_key_id",
      "nonce": "base64_encoded_nonce"
    },
    "content_hash": "sha256_hash_of_original_message",
    "session_id": "SESSION_UUID"
  }'
```

**Response:**
```json
{
  "session_id": "SESSION_UUID",
  "encrypted_response": "base64_encoded_encrypted_response",
  "encryption_metadata": {
    "algorithm": "AES-GCM",
    "key_id": "user_key_id",
    "nonce": "base64_encoded_nonce"
  },
  "content_hash": "sha256_hash_of_original_response",
  "sources": ["source1.pdf", "source2.html"],
  "response_data": {
    "sources": ["source1.pdf", "source2.html"]
  }
}
```

## Get User Sessions
```bash
curl -X GET "http://localhost:8000/api/sessions?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Get Session History
```bash
curl -X GET "http://localhost:8000/api/sessions/SESSION_UUID/history" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "session_id": "SESSION_UUID",
  "history": [
    {
      "id": "message_uuid",
      "sender_type": "user",
      "encrypted_content": "base64_encoded_encrypted_content",
      "encryption_metadata": {
        "algorithm": "AES-GCM",
        "key_id": "user_key_id",
        "nonce": "base64_encoded_nonce"
      },
      "content_hash": "sha256_hash",
      "message_data": null,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

## Update Session Title
```bash
curl -X PUT "http://localhost:8000/api/sessions/SESSION_UUID/title" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

## Delete Session
```bash
curl -X DELETE "http://localhost:8000/api/sessions/SESSION_UUID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Notes

### End-to-End Encryption
- All chat messages are encrypted using AES-GCM encryption
- Each message includes encryption metadata (algorithm, key_id, nonce)
- Content integrity is verified using SHA-256 hashes
- Messages are stored encrypted in the database
- Only the client can decrypt messages using their private key

### Authentication
- Passwords are hashed using bcrypt with salt
- JWT tokens are used for session management
- Login supports both email and phone number
- All protected endpoints require valid JWT token in Authorization header

### Data Privacy
- User data is stored securely in PostgreSQL
- Chat sessions are isolated per user
- No plaintext messages are stored in the database
- All sensitive operations are logged with sanitized data

# 🏗️ Architecture

## File Structure
```
server/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings and environment variables
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy models and Pydantic schemas
├── dependencies.py      # Authentication dependencies
├── init_db.py           # Database initialization
├── rag_pipeline.py      # RAG pipeline for LLM integration
├── session_manager.py   # Chat session management
├── utils/
│   ├── auth.py         # JWT and password utilities
│   ├── encryption.py   # End-to-end encryption utilities
│   ├── logging.py      # Logging middleware and utilities
│   ├── embeddings.py   # Vector embeddings utilities
│   ├── persona.py      # Bot persona management
│   └── vector_store.py # Vector database operations
└── routers/
    ├── auth.py         # Authentication endpoints (/auth)
    └── chat.py         # Protected chat endpoints (/api)
```

## Authentication Flow
1. **Registration**: User creates account → Password hashed with bcrypt → User stored in DB
2. **Login**: User provides email/phone + password → Credentials verified → JWT token generated
3. **Protected Access**: Token included in request → Token validated → User authenticated
4. **Session Management**: User ID extracted from token → Chat sessions created/accessed
5. **Profile Management**: User can update profile information via authenticated endpoints

## Security Implementation

### End-to-End Encryption
- **AES-GCM Encryption**: All chat messages encrypted using AES-GCM algorithm
- **Key Management**: Encryption keys managed client-side with metadata tracking
- **Content Integrity**: SHA-256 hashes verify message integrity
- **Metadata Storage**: Encryption parameters (algorithm, key_id, nonce) stored with messages

### Authentication & Authorization
- **Password Security**: bcrypt hashing with salt for password storage
- **JWT Tokens**: HS256 algorithm with configurable expiration (default 24 hours)
- **Route Protection**: Dependency injection for authentication on protected endpoints
- **Session Isolation**: Users can only access their own chat sessions and data

### Data Privacy
- **Encrypted Storage**: All chat messages stored encrypted in database
- **No Plaintext**: Server never stores unencrypted message content
- **Secure Logging**: Sensitive data sanitized in logs
- **Database Security**: PostgreSQL with connection pooling and health checks

### API Security
- **Input Validation**: Pydantic models validate all request data
- **Error Handling**: Secure error responses without information leakage
- **Rate Limiting**: Built-in FastAPI rate limiting capabilities
- **CORS Protection**: Configurable CORS settings for cross-origin requests

# 🔧 Configuration

## Environment Variables

### Required Variables
```bash
# Database Configuration
export DATABASE_URL="postgresql://postgres:password@localhost:5432/nazarriya"

# JWT Security (REQUIRED - Change in production!)
export SECRET_KEY="your-very-long-random-secret-key-here"
export ACCESS_TOKEN_EXPIRE_MINUTES="1440"  # 24 hours

# LLM Service Configuration
export LLM_SERVICE_URL="http://localhost:8001"

# Application Settings
export DEBUG="False"  # Set to "True" for development
```

### Optional Variables
```bash
# OpenAI Configuration (for LLM service)
export OPENAI_API_KEY="your_openai_api_key"
export OPENAI_MODEL="gpt-3.5-turbo"
export OPENAI_EMBEDDING_MODEL="text-embedding-ada-002"

# Database Configuration
export POSTGRES_PASSWORD="your_secure_password_here"

# RAG Pipeline Settings
export CHUNK_SIZE="1000"
export CHUNK_OVERLAP="200"
export MAX_TOKENS="1000"
```

## JWT Settings
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 24 hours (1440 minutes) - configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Secret Key**: Must be set via `SECRET_KEY` environment variable
- **Token Type**: Bearer token in Authorization header

## Database Integration
- **ORM**: SQLAlchemy 2.0 with async support
- **Database**: PostgreSQL with UUID primary keys
- **Connection Pooling**: Enabled with pre-ping verification
- **Connection Recycling**: Every 5 minutes (300 seconds)
- **Migrations**: Alembic support with version control
- **Data Types**: JSONB for metadata, LargeBinary for encrypted content

## Encryption Configuration
- **Algorithm**: AES-GCM for end-to-end encryption
- **Key Management**: Client-side key generation and management
- **Nonce Generation**: 12-byte random nonces for each message
- **Hash Algorithm**: SHA-256 for content integrity verification
- **Metadata Storage**: JSONB fields for encryption parameters

## LLM Service Integration
- **Service URL**: Configurable via `LLM_SERVICE_URL` (default: http://localhost:8001)
- **Communication**: HTTP REST API with JSON payloads
- **Timeout**: 30 seconds for LLM service requests
- **Fallback**: Graceful degradation with placeholder responses
- **RAG Pipeline**: Integration with vector store and document retrieval

## Production Checklist
- [ ] Change `SECRET_KEY` to strong random value (32+ characters)
- [ ] Set `DEBUG="False"` environment variable
- [ ] Use HTTPS in production with valid SSL certificates
- [ ] Configure proper CORS settings for your domain
- [ ] Set up database connection pooling limits
- [ ] Implement rate limiting and DDoS protection
- [ ] Configure comprehensive logging and monitoring
- [ ] Set up database backups and disaster recovery
- [ ] Regular security audits and dependency updates
- [ ] Configure proper firewall rules
- [ ] Set up health check endpoints
- [ ] Implement proper error handling and alerting

## Security Best Practices
- **Token Management**: Tokens expire automatically, no server-side storage
- **Password Security**: Passwords never stored in plain text, bcrypt hashing
- **Data Isolation**: User sessions and data completely isolated
- **Encrypted Communication**: All chat messages end-to-end encrypted
- **Secure Logging**: Sensitive data sanitized in all logs
- **Input Validation**: All inputs validated using Pydantic models
- **Error Handling**: Secure error responses without information leakage

## Development vs Production

### Development Mode
```bash
export DEBUG="True"
export ACCESS_TOKEN_EXPIRE_MINUTES="1440"  # 24 hours for convenience
```

### Production Mode
```bash
export DEBUG="False"
export ACCESS_TOKEN_EXPIRE_MINUTES="30"    # 30 minutes for security
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

## Debug Mode
Set `export DEBUG="True"` in your environment for:
- Detailed error messages and stack traces
- Auto-reload on code changes
- Enhanced logging output
- Development-friendly error responses

**Warning**: Never use debug mode in production as it exposes sensitive information.
