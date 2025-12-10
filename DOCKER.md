# Docker Development Guide

This guide covers everything you need to know about running Telegram Lead Monitor using Docker.

## Table of Contents

1. [Requirements](#requirements)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Development Workflow](#development-workflow)
5. [Available Commands](#available-commands)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)
8. [Advanced Topics](#advanced-topics)

---

## Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Make** (optional, for convenience commands)

Check your versions:

```bash
docker --version
docker-compose --version
```

---

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository (if you haven't already)
git clone <your-repo-url>
cd telegram-lead-monitor

# Create environment files
make setup
```

### 2. Configure Environment

Edit `backend/.env` with your credentials:

```bash
# Telegram API (required)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# LLM Integration (required for lead analysis)
LLM_API_KEY=your_llm_api_key

# Email settings (optional)
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 3. Start the Application

```bash
make docker-up
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### 5. View Logs

```bash
# All services
make docker-logs

# Specific service
make backend    # Backend logs
make frontend   # Frontend logs
make worker     # Worker logs
```

---

## Architecture

The Docker setup consists of 5 services:

```
┌─────────────────────────────────────────────────┐
│  telegram-monitor-network (Bridge Network)      │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Frontend │  │ Backend  │  │  Worker  │     │
│  │ Next.js  │  │ FastAPI  │  │ Message  │     │
│  │ :3000    │  │ :8000    │  │Collector │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │              │            │
│       └─────────────┼──────────────┘            │
│                     │                           │
│            ┌────────┴────────┐                  │
│            │                 │                  │
│     ┌──────▼─────┐    ┌─────▼────┐            │
│     │ PostgreSQL │    │  Redis   │            │
│     │   :5432    │    │  :6379   │            │
│     └────────────┘    └──────────┘            │
└─────────────────────────────────────────────────┘
```

### Service Details

#### 1. PostgreSQL (postgres)
- **Image**: postgres:15-alpine
- **Port**: 5432
- **Volume**: `telegram-monitor-postgres-data`
- **Purpose**: Main database for users, sources, rules, messages, and leads

#### 2. Redis (redis)
- **Image**: redis:7-alpine
- **Port**: 6379
- **Volume**: `telegram-monitor-redis-data`
- **Purpose**: Caching and session storage

#### 3. Backend (backend)
- **Build**: `backend/Dockerfile` (development target)
- **Port**: 8000
- **Volumes**:
  - `./backend/app:/app/app:ro` (hot reload)
  - `telegram_sessions:/app/sessions` (shared sessions)
- **Purpose**: FastAPI REST API, authentication, business logic

#### 4. Worker (worker)
- **Build**: `backend/Dockerfile` (development target)
- **Command**: `python -m app.workers`
- **Volumes**:
  - `./backend/app:/app/app:ro` (hot reload)
  - `telegram_sessions:/app/sessions` (shared sessions)
- **Purpose**: Background message collection from Telegram sources

#### 5. Frontend (frontend)
- **Build**: `frontend/Dockerfile` (development target)
- **Port**: 3000
- **Volumes**:
  - `./frontend:/app:ro` (hot reload)
  - Anonymous volumes for `node_modules` and `.next`
- **Purpose**: Next.js web interface

---

## Development Workflow

### Hot Reload

All services support hot reload in development mode:

- **Backend**: Uvicorn with `--reload` flag
  - Edit any file in `backend/app/` → automatic restart

- **Frontend**: Next.js dev server
  - Edit any file in `frontend/` → hot module replacement

- **Worker**: Python with module import
  - Edit any file in `backend/app/` → requires manual restart
  - Restart: `docker-compose restart worker`

### Making Code Changes

1. Edit code in your local filesystem
2. Changes are reflected immediately (hot reload)
3. No need to rebuild containers during development

**Example workflow:**

```bash
# Start all services
make docker-up

# Edit backend/app/api/v1/leads.py
# → Backend automatically reloads

# Edit frontend/app/dashboard/page.tsx
# → Frontend automatically updates in browser

# View logs to see reload messages
make backend
```

### Database Migrations

When you modify database models:

```bash
# Generate migration
docker-compose exec backend alembic revision --autogenerate -m "Add new field"

# Apply migration
make migrate
```

### Running Tests

```bash
# Run all backend tests
make test

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py

# Run with coverage
docker-compose exec backend pytest --cov=app tests/
```

---

## Available Commands

### Setup & Start

| Command | Description |
|---------|-------------|
| `make setup` | Create `.env` files from examples |
| `make docker-up` | Build and start all services |
| `make docker-down` | Stop all services |

### Logs

| Command | Description |
|---------|-------------|
| `make docker-logs` | View logs from all services |
| `make backend` | View backend logs only |
| `make frontend` | View frontend logs only |
| `make worker` | View worker logs only |

### Building

| Command | Description |
|---------|-------------|
| `make docker-build` | Build Docker images |
| `make docker-rebuild` | Rebuild images without cache |

### Database

| Command | Description |
|---------|-------------|
| `make migrate` | Run database migrations |
| `make shell-backend` | Open shell in backend container |

### Development

| Command | Description |
|---------|-------------|
| `make test` | Run backend tests |
| `make shell-backend` | Open bash shell in backend |
| `make shell-frontend` | Open sh shell in frontend |
| `make health-check` | Check health of all services |

### Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Remove all containers, volumes, and data |

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Find process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

#### 2. Database Connection Failed

**Error**: `FATAL: password authentication failed for user "telegram_monitor"`

**Solution**:
```bash
# Remove old volumes
docker-compose down -v

# Restart with fresh database
make docker-up
```

#### 3. Backend Won't Start

**Check logs**:
```bash
make backend
```

**Common causes**:
- Missing environment variables in `backend/.env`
- Database not ready (wait for health check)
- Python syntax errors (check logs)

**Solution**:
```bash
# Check backend health
docker-compose exec backend curl localhost:8000/api/health

# Restart backend
docker-compose restart backend
```

#### 4. Frontend Build Fails

**Error**: Module not found or build errors

**Solution**:
```bash
# Rebuild frontend without cache
docker-compose build --no-cache frontend

# Restart frontend
docker-compose restart frontend

# Check logs
make frontend
```

#### 5. Worker Not Collecting Messages

**Check worker logs**:
```bash
make worker
```

**Common causes**:
- Invalid Telegram credentials
- No active sources configured
- Telegram session expired

**Solution**:
```bash
# Check worker is running
docker-compose ps worker

# Restart worker
docker-compose restart worker

# Check Telegram sessions
ls -la backend/sessions/
```

#### 6. Volume Permission Issues

**Error**: Permission denied when accessing volumes

**Solution** (Linux):
```bash
# Set proper ownership
sudo chown -R $USER:$USER backend/sessions

# Or run containers as current user
docker-compose run --user $(id -u):$(id -g) backend bash
```

### Viewing Container Status

```bash
# List running containers
docker-compose ps

# Check resource usage
docker stats

# Inspect specific container
docker-compose logs backend --tail=100
```

### Accessing Container Shell

```bash
# Backend (bash)
make shell-backend

# Frontend (sh)
make shell-frontend

# PostgreSQL
docker-compose exec postgres psql -U telegram_monitor -d telegram_monitor

# Redis
docker-compose exec redis redis-cli
```

### Complete Reset

If everything is broken:

```bash
# Nuclear option: remove everything
make clean

# Start fresh
make docker-up
```

---

## Production Deployment

### Production Configuration

Use the production compose override:

```bash
# Build for production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Key Differences in Production

1. **Build Stage**: Uses production target (optimized)
2. **Workers**: 4 Uvicorn workers for backend
3. **Volumes**: No code mounts (immutable containers)
4. **Restart Policy**: `always` for all services
5. **Nginx**: Added as reverse proxy

### SSL Certificates

For production with nginx:

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your SSL certificates
cp /path/to/fullchain.pem nginx/ssl/
cp /path/to/privkey.pem nginx/ssl/

# Or use Let's Encrypt (recommended)
# See DEPLOYMENT.md for details
```

### Environment Variables for Production

Update `backend/.env` for production:

```env
# Change these in production!
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<generate-strong-32-char-key>
ENCRYPTION_KEY=<generate-fernet-key>

# Use production database URL
DATABASE_URL=postgresql://user:password@prod-db-host:5432/telegram_monitor

# Use production Redis URL
REDIS_URL=redis://prod-redis-host:6379/0

# Production frontend URL
FRONTEND_URL=https://yourdomain.com
CORS_ORIGINS=["https://yourdomain.com"]
```

---

## Advanced Topics

### Custom Worker Interval

Change message collection interval:

```bash
# In backend/.env or docker-compose.yml
WORKER_INTERVAL_MINUTES=10  # Collect every 10 minutes
```

### Scaling Services

Scale backend horizontally:

```bash
# Run 3 backend instances
docker-compose up -d --scale backend=3
```

**Note**: You'll need a load balancer (like nginx) to distribute traffic.

### Debugging Inside Containers

```bash
# Install debugging tools
docker-compose exec backend bash
apt-get update && apt-get install -y iputils-ping curl

# Test connectivity
ping postgres
curl http://backend:8000/api/health
```

### Custom Docker Network

If you need to connect external services:

```bash
# Create external network
docker network create my-custom-network

# Update docker-compose.yml
networks:
  telegram-monitor-network:
    external: true
    name: my-custom-network
```

### Backup & Restore

**Backup PostgreSQL**:
```bash
docker-compose exec postgres pg_dump -U telegram_monitor telegram_monitor > backup.sql
```

**Restore PostgreSQL**:
```bash
cat backup.sql | docker-compose exec -T postgres psql -U telegram_monitor -d telegram_monitor
```

**Backup Telegram Sessions**:
```bash
docker cp telegram-monitor-backend:/app/sessions ./sessions-backup
```

---

## Performance Tuning

### PostgreSQL

Add to `docker-compose.yml`:

```yaml
postgres:
  environment:
    POSTGRES_SHARED_BUFFERS: 256MB
    POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
```

### Redis

Add to `docker-compose.yml`:

```yaml
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Next.js Docker Example](https://github.com/vercel/next.js/tree/canary/examples/with-docker)

---

## Support

If you encounter issues not covered in this guide:

1. Check the main [README.md](./README.md)
2. Review [DEPLOYMENT.md](./DEPLOYMENT.md) for production issues
3. Open an issue on GitHub with:
   - Docker and Docker Compose versions
   - Output of `docker-compose ps`
   - Relevant logs from `make docker-logs`
