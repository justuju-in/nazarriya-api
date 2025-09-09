#!/bin/bash

# Nazarriya API Server Deployment Script for Hetzner Cloud
# This script sets up the server and deploys the Docker services

set -e

echo "🚀 Starting Nazarriya deployment on Hetzner Cloud..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    ufw

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
    
    print_warning "Docker installed successfully!"
    print_warning "Your user has been added to the docker group."
    print_warning "You need to log out and log back in for the group changes to take effect."
    print_warning "After logging back in, run this script again to continue with the deployment."
    print_status "Logging out in 5 seconds..."
    sleep 5
    sudo pkill -KILL -u $USER
else
    print_status "Docker is already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    print_status "Docker Compose is already installed"
fi

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # API server
sudo ufw allow 8001/tcp  # LLM service
sudo ufw allow 5432/tcp  # PostgreSQL (if external access needed)
sudo ufw --force enable

# Create application directory
APP_DIR="/opt/nazarriya"
print_status "Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Set default GitHub username
GITHUB_USERNAME="justuju-in"
print_status "Using default GitHub username: $GITHUB_USERNAME"

# Allow user to override if needed
read -p "Press Enter to use '$GITHUB_USERNAME' as the GitHub username or type a different username: " USER_INPUT
if [ ! -z "$USER_INPUT" ]; then
    GITHUB_USERNAME="$USER_INPUT"
    print_status "Using custom GitHub username: $GITHUB_USERNAME"
fi

# Clone repositories (if not already present)
if [ ! -d "$APP_DIR/nazarriya-api" ]; then
    print_status "Cloning nazarriya-api repository..."
    git clone https://github.com/$GITHUB_USERNAME/nazarriya-api.git $APP_DIR/nazarriya-api
fi

if [ ! -d "$APP_DIR/nazarriya-llm" ]; then
    print_status "Cloning nazarriya-llm repository..."
    git clone https://github.com/$GITHUB_USERNAME/nazarriya-llm.git $APP_DIR/nazarriya-llm
fi

# Set environment variables
print_status "Setting up environment variables..."
ENV_FILE="$APP_DIR/nazarriya-api/.env"
cat > $ENV_FILE << EOF
# Database Configuration
POSTGRES_PASSWORD=your_secure_password_here

# API Server Configuration
# You can use python3 -c "import secrets; print(secrets.token_urlsafe(32))" to generate a 32-byte random key.
SECRET_KEY=your_very_long_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEBUG=False

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# LLM Service Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=1000
EOF

print_warning "Please edit $ENV_FILE and set your actual values before continuing"
print_warning "Press Enter when you're ready to continue..."
read

# Build and start services
print_status "Building and starting Docker services..."
cd $APP_DIR/nazarriya-api

# Pull latest changes for both repositories
print_status "Pulling latest changes for nazarriya-api..."
git pull origin main

print_status "Pulling latest changes for nazarriya-llm..."
cd ../nazarriya-llm
git pull origin main
cd ../nazarriya-api

# Stop any existing services and force rebuild
# This ensures we always use the latest code and prevents issues with outdated Docker images
print_status "Stopping existing services and forcing rebuild..."
docker-compose down

# Start PostgreSQL first
print_status "Starting PostgreSQL..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 20

# Set up the database password properly
print_status "Setting up database authentication..."
POSTGRES_PASSWORD_VALUE=$(grep "^POSTGRES_PASSWORD=" $ENV_FILE | cut -d'=' -f2)
if [ -z "$POSTGRES_PASSWORD_VALUE" ]; then
    print_error "POSTGRES_PASSWORD not found in .env file"
    exit 1
fi

# Create a temporary SQL script to set the password
TEMP_SQL="/tmp/setup_postgres.sql"
cat > $TEMP_SQL << EOF
-- Set the password for the user
ALTER USER nazarriya_user WITH PASSWORD '$POSTGRES_PASSWORD_VALUE';
-- Ensure proper permissions
GRANT ALL PRIVILEGES ON DATABASE nazarriya TO nazarriya_user;
EOF

# Apply the password fix
print_status "Applying database password configuration..."
docker-compose exec -T postgres psql -U nazarriya_user -d nazarriya < $TEMP_SQL

# Clean up temporary file
rm $TEMP_SQL

# Now start the remaining services
print_status "Starting remaining services with rebuild..."
print_status "This will take a few minutes as Docker rebuilds the images with latest code..."
docker-compose up -d --build nazarriya-api nazarriya-llm

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 30

# Check service status
print_status "Checking service status..."
docker-compose ps

# Show logs
print_status "Recent logs from services:"
docker-compose logs --tail=20

print_status "✅ Deployment completed successfully!"
print_status "Services are running on:"
print_status "  - API Server: http://$(curl -s ifconfig.me):8000"
print_status "  - LLM Service: http://$(curl -s ifconfig.me):8001"
print_status "  - PostgreSQL: localhost:5432"
print_status ""
print_status "💡 Note: Services were automatically rebuilt with latest code to ensure all features are available"

print_status "To view logs: docker-compose logs -f"
print_status "To stop services: docker-compose down"
print_status "To restart services: docker-compose restart"
