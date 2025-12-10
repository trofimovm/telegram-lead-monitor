# Deployment Guide

This guide covers deploying Telegram Lead Monitor to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Database Setup](#database-setup)
4. [Deployment Options](#deployment-options)
   - [Docker Compose (Recommended)](#option-1-docker-compose-recommended)
   - [VPS Manual Deployment](#option-2-vps-manual-deployment)
   - [Cloud Platforms](#option-3-cloud-platforms)
5. [Post-Deployment](#post-deployment)
6. [Monitoring](#monitoring)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- [ ] Domain name configured with DNS
- [ ] SSL certificate (Let's Encrypt recommended)
- [ ] PostgreSQL database (14+)
- [ ] Redis instance (7+)
- [ ] SMTP credentials for email notifications
- [ ] Telegram API credentials (from https://my.telegram.org)
- [ ] LLM API key (from llm.codenrock.com or OpenAI)

---

## Environment Variables

### Production Environment Variables

**Backend (.env)**:
```env
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/telegram_monitor

# Redis
REDIS_URL=redis://redis-host:6379/0

# JWT (Generate: openssl rand -hex 32)
SECRET_KEY=your-production-secret-key-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram API
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Encryption (Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your-encryption-key

# LLM
LLM_API_URL=https://llm.codenrock.com
LLM_API_KEY=your-llm-api-key
LLM_MODEL=gpt-4o-mini

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Telegram Lead Monitor

# Application
APP_NAME=Telegram Lead Monitor
ENVIRONMENT=production
DEBUG=False
FRONTEND_URL=https://yourdomain.com
CORS_ORIGINS=["https://yourdomain.com"]
```

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Database Setup

### 1. Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE telegram_monitor;
CREATE USER telegram_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_monitor TO telegram_user;
\q
```

### 2. Run Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

---

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### 1. Create Production docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: telegram_monitor
      POSTGRES_USER: telegram_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: always
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    restart: always
    networks:
      - app-network
    volumes:
      - ./backend/sessions:/app/sessions

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
    ports:
      - "3000:3000"
    restart: always
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: always
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

#### 2. Create Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 3. Create Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]
```

#### 4. Create Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API Docs
        location /docs {
            proxy_pass http://backend/docs;
        }

        location /redoc {
            proxy_pass http://backend/redoc;
        }
    }
}
```

#### 5. Deploy

```bash
# Build and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

---

### Option 2: VPS Manual Deployment

#### 1. Setup Server (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3.10-venv python3-pip \
    postgresql postgresql-contrib redis-server nginx certbot \
    python3-certbot-nginx nodejs npm git

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 2. Setup PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE telegram_monitor;
CREATE USER telegram_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_monitor TO telegram_user;
\q
```

#### 3. Clone and Setup Backend

```bash
# Clone repository
cd /opt
sudo git clone <your-repo-url> telegram-lead-monitor
cd telegram-lead-monitor/backend

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
sudo cp .env.example .env
sudo nano .env  # Edit with production values

# Run migrations
alembic upgrade head
```

#### 4. Setup Backend as systemd Service

Create `/etc/systemd/system/telegram-backend.service`:

```ini
[Unit]
Description=Telegram Lead Monitor Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/telegram-lead-monitor/backend
Environment="PATH=/opt/telegram-lead-monitor/backend/venv/bin"
ExecStart=/opt/telegram-lead-monitor/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-backend
sudo systemctl start telegram-backend
sudo systemctl status telegram-backend
```

#### 5. Setup Frontend

```bash
cd /opt/telegram-lead-monitor/frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
nano .env.local  # Edit with production values

# Build
npm run build
```

#### 6. Setup Frontend as systemd Service

Create `/etc/systemd/system/telegram-frontend.service`:

```ini
[Unit]
Description=Telegram Lead Monitor Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/telegram-lead-monitor/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-frontend
sudo systemctl start telegram-frontend
sudo systemctl status telegram-frontend
```

#### 7. Configure Nginx

Create `/etc/nginx/sites-available/telegram-monitor`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable site and get SSL:

```bash
sudo ln -s /etc/nginx/sites-available/telegram-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

---

### Option 3: Cloud Platforms

#### Heroku

1. Create `Procfile` in backend:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
release: alembic upgrade head
```

2. Deploy:
```bash
heroku create telegram-monitor-backend
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

#### AWS / DigitalOcean / Linode

Follow the VPS manual deployment guide above. Most cloud VPS providers offer similar Ubuntu environments.

#### Vercel (Frontend Only)

```bash
cd frontend
vercel --prod
```

Set environment variables in Vercel dashboard.

---

## Post-Deployment

### 1. Create Admin User

```bash
# Connect to your production database
psql $DATABASE_URL

# Update a user to be superuser
UPDATE users SET is_superuser = true WHERE email = 'admin@yourdomain.com';
```

### 2. Test API

```bash
curl https://api.yourdomain.com/api/v1/auth/me
```

### 3. Configure Monitoring

- Setup error tracking (Sentry)
- Configure uptime monitoring (UptimeRobot, Pingdom)
- Enable application logging

---

## Monitoring

### Application Logs

**Docker**:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Systemd**:
```bash
sudo journalctl -u telegram-backend -f
sudo journalctl -u telegram-frontend -f
```

### Database Monitoring

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Monitor active connections
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"
```

### Redis Monitoring

```bash
redis-cli info
redis-cli monitor
```

---

## Backup & Recovery

### Database Backup

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > /backups/telegram_monitor_$DATE.sql
```

Setup cron job:
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

### Restore from Backup

```bash
psql $DATABASE_URL < backup_file.sql
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend
# or
sudo journalctl -u telegram-backend -n 100

# Common issues:
# - Database connection: Check DATABASE_URL
# - Missing migrations: Run alembic upgrade head
# - Port conflict: Check if port 8000 is in use
```

### Frontend Won't Build

```bash
# Check Node version
node --version  # Should be 18+

# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL

# Check PostgreSQL is running
sudo systemctl status postgresql
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

---

## Security Checklist

- [ ] All environment variables are set securely
- [ ] SSL/TLS is configured correctly
- [ ] Database has strong password
- [ ] Firewall is configured (only ports 80, 443, 22 open)
- [ ] SSH key authentication enabled (password auth disabled)
- [ ] Regular security updates enabled
- [ ] Backups are automated and tested
- [ ] CORS is configured restrictively
- [ ] Rate limiting is enabled (if implemented)
- [ ] Logging and monitoring are active

---

## Scaling Considerations

### Horizontal Scaling

- Use load balancer (nginx, HAProxy)
- Deploy multiple backend instances
- Use managed database (AWS RDS, DigitalOcean Managed DB)
- Use Redis Cluster for session storage

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database queries
- Add database indexes
- Enable query caching

---

## Support

For deployment support:
- Email: [your-email]
- Documentation: https://docs.yourdomain.com

---

**Last Updated**: 2024-01-01
