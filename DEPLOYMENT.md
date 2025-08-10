# Deployment Guide

## Production Deployment

### 1. Environment Setup

Create a `.env` file with production values:

```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/taskmanager
PORT=5000
```

### 2. Database Setup

For PostgreSQL (recommended for production):

```sql
-- Create database
CREATE DATABASE taskmanager;
CREATE USER taskmanager_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskmanager_user;
```

### 3. Install Production Dependencies

```bash
pip install gunicorn psycopg2-binary
```

### 4. Run Migrations

```bash
flask db upgrade
```

### 5. Start with Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://taskmanager:password@db:5432/taskmanager
      - SECRET_KEY=your-secret-key
      - JWT_SECRET_KEY=your-jwt-secret
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=taskmanager
      - POSTGRES_USER=taskmanager
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

1. **Use HTTPS in production**
2. **Set strong SECRET_KEY and JWT_SECRET_KEY**
3. **Use environment variables for sensitive data**
4. **Enable CORS if needed for frontend integration**
5. **Set up proper database backups**
6. **Use a reverse proxy (Nginx)**
7. **Set up monitoring and logging**

## Monitoring

### Health Check

The API provides a health check endpoint at `/` that returns:

```json
{
    "status": "ok",
    "message": "Task Manager API is running!",
    "version": "1.0.0",
    "description": "RESTful API for task management with JWT authentication",
    "environment": "production"
}
```

### Logging

For production logging, add to your configuration:

```python
import logging

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = logging.FileHandler('logs/taskmanager.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

## Performance Optimization

1. **Use Redis for session storage**
2. **Implement caching for frequent queries**
3. **Set up database connection pooling**
4. **Use CDN for static assets**
5. **Implement rate limiting**

## Backup Strategy

```bash
# Database backup (PostgreSQL)
pg_dump taskmanager > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/var/backups/taskmanager"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump taskmanager > $BACKUP_DIR/taskmanager_$DATE.sql
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```
