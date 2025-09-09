# Nazarriya Deployment Guide for Hetzner Cloud

This guide covers deploying both the Nazarriya API server and LLM service on Hetzner Cloud using Docker.

## Prerequisites

- Hetzner Cloud account
- Domain name (optional but recommended)
- SSH access to your server
- Basic knowledge of Linux commands

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App  │    │   Nginx/Proxy   │    │  Docker Host    │
│                 │    │                 │    │                 │
│ nazarriya-ui   │◄──►│   SSL/HTTPS     │◄──►│ ┌─────────────┐ │
└─────────────────┘    └─────────────────┘    │ │ PostgreSQL  │ │
                                              │ │ Port: 5432  │ │
                                              │ └─────────────┘ │
                                              │ ┌─────────────┐ │
                                              │ │ API Server  │ │
                                              │ │ Port: 8000  │ │
                                              │ └─────────────┘ │
                                              │ ┌─────────────┐ │
                                              │ │ LLM Service │ │
                                              │ │ Port: 8001  │ │
                                              │ └─────────────┘ │
                                              └─────────────────┘
```

## Server Requirements

- **CPU**: 2+ cores (CX21 or higher)
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 40GB+ SSD
- **OS**: Ubuntu 22.04 LTS

## Quick Deployment

### 1. Create Hetzner Server

1. Log into [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Create a new project
3. Add a new server:
   - Choose Ubuntu 22.04 LTS
   - Select CX21 or higher
   - Choose your preferred location
   - Add your SSH key
   - Note down the server IP

### 2. Initial Server Setup

```bash
# SSH into your server
ssh ubuntu@YOUR_SERVER_IP # This assumes that you have applied Justuju's cloud config file
```

### 3. Run Deployment Script

```bash
# Download and run the deployment script
curl -O https://raw.githubusercontent.com/justuju-in/nazarriya-api/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Install Docker and Docker Compose
- Configure firewall rules
- Clone repositories
- Set up environment variables
- Build and start services

### 4. Configure Environment Variables

Edit the `.env` file created by the script:

```bash
nano /opt/nazarriya/.env
```

Set these required values:
```env
# Database
POSTGRES_PASSWORD=your_secure_password_here

# API Server
SECRET_KEY=your_very_long_random_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEBUG=False

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# LLM Service
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=1000
```

### 5. Ingest documents

```bash
cd /opt/nazarriya/nazarriya-api
docker-compose exec nazarriya-llm bash -c "python ingest_documents.py data/pdfs/*.pdf data/html/*.html"
```

## Manual Deployment Steps

If you prefer to deploy manually:

### 1. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone Repositories

```bash
# Create application directory
sudo mkdir -p /opt/nazarriya
sudo chown $USER:$USER /opt/nazarriya

# Clone repositories
cd /opt/nazarriya
git clone https://github.com/justuju-in/nazarriya-api.git
git clone https://github.com/justuju-in/nazarriya-llm.git
```

### 3. Configure and Start Services

```bash
cd nazarriya-api

# Copy and edit environment file
cp .env.example .env
nano .env

# Build and start services
docker-compose up -d --build
```

## Service Management

### View Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nazarriya-api
docker-compose logs -f nazarriya-llm
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart nazarriya-api
```

### Stop Services

```bash
docker-compose down
```

### Update Services

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

## Database Management

### Run Migrations

```bash
# Enter the API container
docker-compose exec nazarriya-api bash

# Run migrations
alembic upgrade head
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U nazarriya_user nazarriya > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T postgres psql -U nazarriya_user nazarriya < backup_file.sql
```

## SSL and Domain Setup

### 1. Install Nginx

```bash
sudo apt install -y nginx
```

### 2. Configure Nginx

**Note**: Make sure to replace your-domain.com with your actual address.

Create `/etc/nginx/sites-available/nazarriya`:

```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /llm/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable Site and SSL

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/nazarriya /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Maintenance

### Health Checks

Services include health checks that can be monitored:

- API Server: `http://localhost:8000/`
- LLM Service: `http://localhost:8001/health`
- PostgreSQL: Internal health check

### Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/nazarriya

# Add configuration
/opt/nazarriya/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 nazarriya nazarriya
}
```

### Backup Strategy

1. **Database**: Daily automated backups
2. **Application**: Git-based deployment
3. **Configuration**: Version controlled
4. **Logs**: Rotated and archived

## Troubleshooting

### Common Issues

1. **Port already in use**: Check if services are running on the same ports
2. **Database connection failed**: Verify PostgreSQL is running and credentials are correct
3. **Permission denied**: Check file permissions and Docker group membership
4. **Build failures**: Ensure all dependencies are available

### Debug Commands

```bash
# Check Docker status
docker ps -a
docker images

# Check service logs
docker-compose logs

# Check system resources
htop
df -h
free -h

# Check network
netstat -tlnp
```

## Security Considerations

1. **Firewall**: Only expose necessary ports
2. **SSL**: Use HTTPS for all external communication
3. **Secrets**: Store sensitive data in environment variables
4. **Updates**: Regularly update system and Docker images
5. **Backups**: Implement automated backup procedures

## Scaling Considerations

For production workloads:

1. **Load Balancer**: Use Hetzner Load Balancer for multiple instances
2. **Database**: Consider managed PostgreSQL service
3. **Monitoring**: Implement proper monitoring and alerting
4. **Auto-scaling**: Use Docker Swarm or Kubernetes for orchestration

## Support

For deployment issues:

1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Check network connectivity
4. Review firewall rules
5. Ensure sufficient system resources

---

**Note**: This deployment guide assumes you have the necessary permissions and access to your Hetzner Cloud account. Always follow security best practices and keep your systems updated.
