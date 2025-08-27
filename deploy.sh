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
    print_warning "Docker installed. You may need to log out and back in for group changes to take effect."
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

# Clone repositories (if not already present)
if [ ! -d "$APP_DIR/nazarriya-api" ]; then
    print_status "Cloning nazarriya-api repository..."
    git clone https://github.com/yourusername/nazarriya-api.git $APP_DIR/nazarriya-api
fi

if [ ! -d "$APP_DIR/nazarriya-llm" ]; then
    print_status "Cloning nazarriya-llm repository..."
    git clone https://github.com/yourusername/nazarriya-llm.git $APP_DIR/nazarriya-llm
fi

# Set environment variables
print_status "Setting up environment variables..."
ENV_FILE="$APP_DIR/.env"
cat > $ENV_FILE << EOF
# Database Configuration
POSTGRES_PASSWORD=your_secure_password_here

# API Server Configuration
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

# Pull latest changes
git pull origin main

# Build and start services
print_status "Starting services with Docker Compose..."
docker-compose up -d --build

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

print_status "To view logs: docker-compose logs -f"
print_status "To stop services: docker-compose down"
print_status "To restart services: docker-compose restart"
