# Deployment Guide

## Production Deployment with Docker

### Prerequisites
- Docker installed
- Docker Compose installed
- Domain name (optional)
- SSL certificate (for HTTPS)

### Step 1: Configure Environment Variables

Create `.env.production`:

```env
# Django
SECRET_KEY=your-very-secure-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=exam_checker_db
DB_USER=postgres
DB_PASSWORD=very-secure-password
DB_HOST=db
DB_PORT=5432

# OpenAI
OPENAI_API_KEY=your-production-openai-api-key

# Celery & Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=another-very-secure-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# File Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,txt,jpg,jpeg,png

# SBERT
SBERT_MODEL_NAME=all-MiniLM-L6-v2

# GPT
GPT_MODEL=gpt-4-turbo-preview
GPT_MAX_TOKENS=1000
GPT_TEMPERATURE=0.3

# Evaluation Weights
SIMILARITY_WEIGHT=0.6
CONTEXT_WEIGHT=0.4
```

### Step 2: Build and Run

```bash
docker-compose up -d --build
```

### Step 3: Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### Step 4: Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### Step 5: Collect Static Files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

## Deploy to AWS

### Using AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t3.medium or larger (for AI models)
   - Security group: Allow ports 80, 443, 22

2. **Install Docker**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo usermod -aG docker ubuntu
   ```

3. **Clone Repository**
   ```bash
   git clone <your-repo>
   cd AI-Powered\ Exam\ Checker
   ```

4. **Configure and Deploy**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   docker-compose up -d --build
   ```

### Using AWS Elastic Beanstalk

1. Install EB CLI
2. Initialize EB application
3. Deploy

```bash
eb init
eb create exam-checker-env
eb deploy
```

## Deploy to Render

### Web Service Deployment

1. Connect your GitHub repository to Render
2. Create new Web Service
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn exam_checker.wsgi:application`
   - **Environment Variables**: Add all from `.env`

### Database

1. Create PostgreSQL instance on Render
2. Copy connection string to environment variables

### Redis

1. Create Redis instance on Render
2. Copy connection URL to `CELERY_BROKER_URL`

## Deploy to Railway

1. Connect GitHub repository
2. Add PostgreSQL database
3. Add Redis
4. Add environment variables
5. Deploy automatically

## Nginx Configuration (Production)

Create `nginx.conf`:

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    client_max_body_size 10M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }
}
```

## SSL/HTTPS Setup with Let's Encrypt

```bash
docker-compose exec web certbot --nginx -d yourdomain.com
```

## Monitoring and Logging

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs celery

# Follow logs
docker-compose logs -f web
```

### Database Backup

```bash
docker-compose exec db pg_dump -U postgres exam_checker_db > backup.sql
```

### Restore Database

```bash
docker-compose exec -T db psql -U postgres exam_checker_db < backup.sql
```

## Performance Optimization

1. **Enable Caching**
   - Redis for Django cache
   - Model caching for SBERT

2. **CDN for Static Files**
   - Use AWS S3 + CloudFront
   - Or Cloudflare

3. **Database Optimization**
   - Indexes on frequently queried fields
   - Connection pooling

4. **Celery Workers**
   - Multiple workers for parallel processing
   - Priority queues for urgent tasks

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  web:
    deploy:
      replicas: 3
```

### Load Balancing

Use Nginx or AWS ELB for load balancing across multiple instances.

## Security Checklist

- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Set secure cookies
- [ ] Configure CORS properly
- [ ] Use strong database passwords
- [ ] Rotate API keys regularly
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Regular security updates

## Cost Estimation

### AWS (Monthly)
- EC2 t3.medium: ~$30
- RDS PostgreSQL: ~$15
- ElastiCache Redis: ~$13
- S3 + CloudFront: ~$5
- **Total**: ~$63/month

### Render
- Web Service: $7/month
- PostgreSQL: $7/month
- Redis: $7/month
- **Total**: ~$21/month

### Railway
- Similar to Render: ~$20-25/month

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip install -U -r requirements.txt
   ```

2. **Clean Guest Files**
   - Automated with Celery beat task
   - Runs every 24 hours

3. **Monitor Disk Space**
   ```bash
   docker system df
   docker system prune
   ```

4. **Database Vacuum**
   ```bash
   docker-compose exec db vacuumdb -U postgres exam_checker_db
   ```

## Troubleshooting Production Issues

### High Memory Usage
- Increase server RAM
- Reduce Celery workers
- Implement model caching

### Slow Evaluations
- Scale Celery workers
- Use faster GPU instances
- Optimize GPT prompts

### Database Locks
- Check slow queries
- Add indexes
- Increase connection pool

---

For production support, monitor logs regularly and set up alerts for errors.
