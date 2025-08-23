@echo off
setlocal enabledelayedexpansion

echo 🚀 Setting up NazarRiya Database...

REM Find PostgreSQL tools
set "POSTGRES_PATH="
for %%i in (
    "C:\Program Files\PostgreSQL\15\bin"
    "C:\Program Files\PostgreSQL\16\bin"
    "C:\Program Files (x86)\PostgreSQL\15\bin"
    "C:\Program Files (x86)\PostgreSQL\16\bin"
) do (
    if exist "%%i\psql.exe" (
        set "POSTGRES_PATH=%%i"
        goto :found_postgres
    )
)

:not_found
echo ❌ PostgreSQL command-line tools not found!
echo.
echo Please install PostgreSQL first:
echo Download from https://www.postgresql.org/download/windows/
echo.
echo After installation, ensure the PostgreSQL tools are in your PATH
pause
exit /b 1

:found_postgres
echo ✅ Found PostgreSQL tools in: %POSTGRES_PATH%

REM Check if PostgreSQL is running
echo 🔍 Checking if PostgreSQL is running...
"%POSTGRES_PATH%\pg_isready.exe" -h localhost -p 5432 >nul 2>&1
if errorlevel 1 (
    echo ❌ PostgreSQL is not running on port 5432
    echo.
    echo Please start PostgreSQL:
    echo - Through Windows Services
    echo - Or start the PostgreSQL service manually
    pause
    exit /b 1
)

echo ✅ PostgreSQL is running on port 5432

REM Create database
echo 📦 Creating database 'nazarriya'...
"%POSTGRES_PATH%\createdb.exe" -h localhost -U postgres nazarriya
if errorlevel 1 (
    echo ❌ Failed to create database. Please check your PostgreSQL credentials.
    pause
    exit /b 1
)

echo ✅ Database 'nazarriya' created successfully

REM Install Python dependencies
echo 📚 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    echo You may need to upgrade pip: pip install --upgrade pip
    pause
    exit /b 1
)

REM Initialize Alembic
echo 🔧 Initializing Alembic...
if not exist "alembic" (
    alembic init alembic
) else (
    echo Alembic already initialized
)

REM Update alembic.ini with correct database URL
echo 🔧 Updating Alembic configuration...
powershell -Command "(Get-Content alembic.ini) -replace 'sqlalchemy.url = .*', 'sqlalchemy.url = postgresql://postgres@localhost:5432/nazarriya' | Set-Content alembic.ini"

REM Create initial migration
echo 📝 Creating initial migration...
alembic revision --autogenerate -m "Initial migration"
if errorlevel 1 (
    echo ❌ Failed to create migration. Please check your models and database connection.
    pause
    exit /b 1
)

REM Run migrations
echo 🚀 Running database migrations...
alembic upgrade head
if errorlevel 1 (
    echo ❌ Failed to run migrations. Please check the error messages above.
    pause
    exit /b 1
)

REM Initialize database with sample data
echo 🎯 Initializing database with sample data...
cd server
python init_db.py
if errorlevel 1 (
    echo ❌ Failed to initialize sample data. Please check the error messages above.
    pause
    exit /b 1
)
cd ..

echo ✅ Database setup complete!
echo.
echo 📋 Next steps:
echo 1. Update your environment variables in .env file
echo 2. Start implementing JWT authentication
echo 3. Update the chat router to use the database
echo.
echo 🌐 You can now start your server with:
echo    cd server ^&^& uvicorn main:app --reload

pause
