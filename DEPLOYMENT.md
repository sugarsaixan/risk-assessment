# Risk Assessment Deployment Guide

Deploy to `aisys.agula.mn/assessment/`

## Prerequisites

- Docker & Docker Compose installed
- Traefik reverse proxy running
- Networks `traefik` and `production` exist

## 1. Clone and Configure

```bash
# Clone repository to server
git clone <repo-url> /opt/risk-assessment
cd /opt/risk-assessment

# Create environment file
cp .env.example .env

# Edit with production values
nano .env
```

**.env contents:**
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=risk_assessment
PUBLIC_URL=https://aisys.agula.mn/assessment
CORS_ORIGINS=https://aisys.agula.mn
```

## 2. Build Images

```bash
docker-compose build
```

## 3. Deploy

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 4. Run Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

## 5. Verify Deployment

```bash
# Health check
curl https://aisys.agula.mn/assessment/api/health

# Frontend
curl -I https://aisys.agula.mn/assessment/
```

## URLs

| Service | URL |
|---------|-----|
| Frontend | https://aisys.agula.mn/assessment/ |
| API | https://aisys.agula.mn/assessment/api/ |
| Health | https://aisys.agula.mn/assessment/api/health |
| API Docs | https://aisys.agula.mn/assessment/api/docs |

## Common Commands

```bash
# Restart services
docker-compose restart

# Stop services
docker-compose down

# View API logs
docker-compose logs -f api

# View frontend logs
docker-compose logs -f frontend

# Rebuild and restart
docker-compose up -d --build

# Database shell
docker-compose exec postgres psql -U postgres -d risk_assessment
```

## Troubleshooting

**502 Bad Gateway:**
```bash
# Check if containers are running
docker-compose ps

# Check API logs
docker-compose logs api
```

**Database connection error:**
```bash
# Check postgres is healthy
docker-compose exec postgres pg_isready -U postgres

# Verify DATABASE_URL in api container
docker-compose exec api env | grep DATABASE
```

**Frontend not loading:**
```bash
# Check nginx config
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Check if files exist
docker-compose exec frontend ls -la /usr/share/nginx/html/assessment/
```

## Update Deployment

```bash
cd /opt/risk-assessment
git pull
docker-compose up -d --build
docker-compose exec api alembic upgrade head
```
