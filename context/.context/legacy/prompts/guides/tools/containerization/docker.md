---
name: Docker Development Guide
module_type: guide
scope: temporary
priority: low
triggers: ["docker", "dockerfile", "docker-compose", "container", "containerization", "docker build"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Docker Development Guide

## Purpose
Master Docker for development environments, from basic containerization to multi-service orchestration with docker-compose, including best practices for security and optimization.

## Installation and Setup
```bash
# Verify installation
docker --version
docker-compose --version

# Check Docker daemon
docker info

# Test installation
docker run hello-world

# Configure Docker without sudo (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

## Dockerfile Basics

### Simple Dockerfile
```dockerfile
# Basic Node.js application
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Define startup command
CMD ["node", "server.js"]
```

### Multi-stage Build
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Python Application
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run application
CMD ["python", "app.py"]
```

## Building and Running Containers

### Build Commands
```bash
# Basic build
docker build -t myapp .

# Build with specific Dockerfile
docker build -f Dockerfile.dev -t myapp:dev .

# Build with build args
docker build --build-arg VERSION=1.2.3 -t myapp:1.2.3 .

# Build without cache
docker build --no-cache -t myapp .

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t myapp .
```

### Run Commands
```bash
# Basic run
docker run myapp

# Run with port mapping
docker run -p 8080:3000 myapp

# Run in background
docker run -d --name myapp-container myapp

# Run with environment variables
docker run -e NODE_ENV=production -e API_KEY=secret myapp

# Run with volume mount
docker run -v $(pwd)/data:/app/data myapp

# Run interactively
docker run -it ubuntu bash

# Run with resource limits
docker run --memory="512m" --cpus="1.5" myapp
```

## Docker Compose

### Basic docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
    depends_on:
      - db
    volumes:
      - ./src:/app/src  # Hot reload

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Advanced Compose Features
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
      args:
        - BUILD_ENV=development
    command: npm run dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    env_file:
      - .env.local
    depends_on:
      db:
        condition: service_healthy
    networks:
      - frontend
      - backend
    restart: unless-stopped

  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app
    networks:
      - frontend

networks:
  frontend:
  backend:

volumes:
  postgres_data:
  redis_data:
```

### Compose Commands
```bash
# Start services
docker-compose up
docker-compose up -d  # Detached

# Start specific services
docker-compose up web db

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down
docker-compose down -v  # Remove volumes too

# View logs
docker-compose logs
docker-compose logs -f web  # Follow specific service

# Execute commands
docker-compose exec web bash
docker-compose exec db psql -U postgres

# Scale services
docker-compose up --scale worker=3
```

## Volume Management

### Types of Volumes
```bash
# Named volumes (managed by Docker)
docker volume create mydata
docker run -v mydata:/data myapp

# Bind mounts (host directory)
docker run -v /host/path:/container/path myapp
docker run -v $(pwd):/app myapp

# Anonymous volumes
docker run -v /data myapp

# Read-only volumes
docker run -v $(pwd)/config:/config:ro myapp
```

### Volume Commands
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect mydata

# Remove volume
docker volume rm mydata

# Remove unused volumes
docker volume prune

# Backup volume
docker run --rm -v mydata:/source -v $(pwd):/backup alpine \
  tar czf /backup/mydata-backup.tar.gz -C /source .

# Restore volume
docker run --rm -v mydata:/target -v $(pwd):/backup alpine \
  tar xzf /backup/mydata-backup.tar.gz -C /target
```

## Network Management

### Network Types
```bash
# Bridge network (default)
docker network create mynetwork

# Host network (Linux only)
docker run --network host myapp

# None network (isolated)
docker run --network none myapp

# Connect container to network
docker network connect mynetwork mycontainer

# Custom bridge with subnet
docker network create --subnet=172.20.0.0/16 mynetwork
```

### Network Commands
```bash
# List networks
docker network ls

# Inspect network
docker network inspect bridge

# Remove network
docker network rm mynetwork

# Remove unused networks
docker network prune
```

## Development Workflows

### Hot Reload Setup
```dockerfile
# Dockerfile.dev
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
# Don't copy source - will be mounted

CMD ["npm", "run", "dev"]
```

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - ./src:/app/src
      - ./public:/app/public
      - /app/node_modules  # Preserve container's node_modules
    ports:
      - "3000:3000"
    environment:
      - CHOKIDAR_USEPOLLING=true  # For file watching
```

### Database Development
```yaml
# Local database with initialization
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: devpass
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  adminer:
    image: adminer
    ports:
      - "8080:8080"
    depends_on:
      - postgres
```

## Best Practices

### Security
```dockerfile
# Use specific versions
FROM node:18.17.1-alpine

# Run as non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001
USER nodejs

# Copy only necessary files
COPY --chown=nodejs:nodejs package*.json ./
RUN npm ci --only=production
COPY --chown=nodejs:nodejs . .

# Use secrets properly
# Bad:
# ENV API_KEY=secret123

# Good: Use runtime secrets
# docker run --secret api_key myapp
```

### Optimization
```dockerfile
# Order layers by change frequency
FROM node:18-alpine

# System dependencies (rarely change)
RUN apk add --no-cache python3 make g++

# Application dependencies (change occasionally)
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Application code (changes frequently)
COPY . .

# Use .dockerignore
# node_modules
# .git
# .env
# coverage
# .DS_Store
```

### Layer Caching
```dockerfile
# Optimize for caching
# Bad: Invalidates cache on any file change
COPY . .
RUN npm install

# Good: Cache dependencies separately
COPY package*.json ./
RUN npm ci
COPY . .
```

## Debugging Containers

### Interactive Debugging
```bash
# Debug running container
docker exec -it container_name bash

# Start new container for debugging
docker run -it --entrypoint /bin/sh myapp

# Debug with specific command
docker run -it myapp /bin/bash -c "ls -la && pwd"

# Attach to running container
docker attach container_name

# View container processes
docker top container_name
```

### Logs and Inspection
```bash
# View logs
docker logs container_name
docker logs -f container_name  # Follow
docker logs --tail 50 container_name

# Inspect container
docker inspect container_name

# View specific config
docker inspect container_name | jq '.[0].Config.Env'

# Monitor resource usage
docker stats
docker stats container_name
```

## Container Registry

### Working with Registries
```bash
# Docker Hub
docker login
docker tag myapp username/myapp:latest
docker push username/myapp:latest

# Private registry
docker login registry.company.com
docker tag myapp registry.company.com/myapp:latest
docker push registry.company.com/myapp:latest

# Pull specific version
docker pull nginx:1.21.6-alpine

# Export/Import images
docker save myapp > myapp.tar
docker load < myapp.tar
```

## Cleanup Commands

### System Cleanup
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune
docker image prune -a  # All unused images

# Remove everything unused
docker system prune
docker system prune -a --volumes

# View disk usage
docker system df

# Remove specific types
docker rm $(docker ps -aq)  # All containers
docker rmi $(docker images -q)  # All images
```

## Common Patterns

### Multi-Service Development
```yaml
# Full stack application
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

  api:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  worker:
    build: ./backend
    command: python worker.py
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - api
```

---
*Docker simplifies development environments, ensures consistency across teams, and streamlines the path from development to production.*