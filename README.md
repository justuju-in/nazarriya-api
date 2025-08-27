# nazarriya-backend
NazarRiya web server


## Developer instructions

### 0. Setup
*Note: Latest code and instructions are in the "development" branch which will
      periodically be merged to main after reaching specific milestones and
      performing all regression tests.*


Clone repo: `git clone git@github.com:paulrahul/nazarriya-backend.git`
Install dependencies: `pip install -r requirements.txt`
Install PostgreSQL

### 1. Environment Variables
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

### 2. Setup DB
```bash
# Run *.bat for Windows or .sh for Linux but if you have Python, then running the .py script is the best option.
python database/setup_database.py
```

### 2. Run server
```bash
uvicorn server.main:app --reload
```

### 3. Test Authentication
```bash
# Test the complete authentication system
python test/test_auth.py
```

### 4. API Usage Examples

### User Registration
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

### User Login
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

### Get Current User Profile
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Create a New Chat Session
```bash
curl -X POST "http://localhost:8000/chat/sessions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My New Chat"}'
```

### Send a Chat Message
```bash
curl -X POST "http://localhost:8000/chat/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "session_id": "SESSION_UUID"}'
```

### Get User Sessions
```bash
curl -X GET "http://localhost:8000/chat/sessions?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Session History
```bash
curl -X GET "http://localhost:8000/chat/sessions/SESSION_UUID/history" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update Session Title
```bash
curl -X PUT "http://localhost:8000/chat/sessions/SESSION_UUID/title" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

### Delete Session
```bash
curl -X DELETE "http://localhost:8000/chat/sessions/SESSION_UUID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🏗️ Architecture

### File Structure
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

### Authentication Flow
1. **Registration**: User creates account → Password hashed → User stored in DB
2. **Login**: User provides credentials → Password verified → JWT token generated
3. **Protected Access**: Token included in request → Token validated → User authenticated
4. **Session Management**: User ID extracted from token → Chat sessions created/accessed

### Security Implementation
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: HS256 algorithm, configurable expiration
- **Route Protection**: Dependency injection for authentication
- **Database Sessions**: Secure session management with PostgreSQL

## 🔧 Configuration

### JWT Settings
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 30 minutes (configurable)
- **Secret Key**: Environment variable (change in production)

### Database Integration
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Connection Pooling**: Enabled with health checks
- **Migrations**: Alembic support

### Production Checklist
- [ ] Change `SECRET_KEY` environment variable to strong random value
- [ ] Set `DEBUG=False` environment variable
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Add comprehensive logging
- [ ] Regular security audits

### Best Practices
- Tokens expire automatically
- Passwords are never stored in plain text
- User sessions are isolated
- Database connections are pooled and secured

### Debug Mode
Set `export DEBUG="True"` in your environment for detailed error messages and auto-reload.
