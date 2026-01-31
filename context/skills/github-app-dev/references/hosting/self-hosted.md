# Self-Hosted GitHub Apps

Run GitHub Apps on your own infrastructure for maximum control and compliance.

## Why Self-Host?

| Advantage | Details |
|-----------|---------|
| Full control | Complete customization |
| Compliance | Meet regulatory requirements |
| Data sovereignty | Keep data on-premise |
| Cost at scale | Predictable costs for high volume |
| Private networks | Access internal resources |

## Limitations

- **Operational overhead** - You manage everything
- **Security responsibility** - Patching, updates, monitoring
- **Scaling complexity** - Manual or self-managed auto-scaling
- **No managed services** - BYO databases, caching, etc.

## Deployment Options

| Option | Complexity | Best For |
|--------|------------|----------|
| Docker Compose | Low | Small teams, simple apps |
| Kubernetes | High | Large scale, HA requirements |
| VM + PM2 | Medium | Traditional ops teams |

## Docker Compose Setup

### Project Structure

```
my-github-app/
├── src/
│   ├── index.ts
│   ├── webhooks.ts
│   └── github.ts
├── docker/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── package.json
└── .env.example
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - DATABASE_URL=postgres://github_app:password@db:5432/github_app
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=github_app
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=github_app
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U github_app"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist

USER nodejs

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/s;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        location /webhook {
            limit_req zone=webhook burst=20 nodelay;

            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://app;
        }
    }
}
```

## Kubernetes Setup

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: github-app
  labels:
    app: github-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: github-app
  template:
    metadata:
      labels:
        app: github-app
    spec:
      containers:
        - name: app
          image: your-registry/github-app:latest
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: production
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: github-app-secrets
                  key: database-url
            - name: GITHUB_APP_ID
              valueFrom:
                secretKeyRef:
                  name: github-app-secrets
                  key: app-id
            - name: GITHUB_PRIVATE_KEY
              valueFrom:
                secretKeyRef:
                  name: github-app-secrets
                  key: private-key
            - name: GITHUB_WEBHOOK_SECRET
              valueFrom:
                secretKeyRef:
                  name: github-app-secrets
                  key: webhook-secret
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: github-app
spec:
  selector:
    app: github-app
  ports:
    - port: 80
      targetPort: 3000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: github-app
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - your-domain.com
      secretName: github-app-tls
  rules:
    - host: your-domain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: github-app
                port:
                  number: 80
```

### secrets.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: github-app-secrets
type: Opaque
stringData:
  app-id: "123456"
  private-key: |
    -----BEGIN RSA PRIVATE KEY-----
    ...
    -----END RSA PRIVATE KEY-----
  webhook-secret: "your-secret"
  database-url: "postgres://user:pass@host:5432/db"
```

### HorizontalPodAutoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: github-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: github-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

## VM Setup (PM2)

### Setup Script

```bash
#!/bin/bash
set -e

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database
sudo -u postgres createuser github_app
sudo -u postgres createdb -O github_app github_app

# Install Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server

# Install Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Clone and setup app
git clone https://github.com/your-org/your-repo.git /opt/github-app
cd /opt/github-app
npm ci --production
npm run build

# Create .env file
cat > .env << 'EOF'
NODE_ENV=production
PORT=3000
DATABASE_URL=postgres://github_app:password@localhost:5432/github_app
REDIS_URL=redis://localhost:6379
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="..."
GITHUB_WEBHOOK_SECRET=your-secret
EOF

# Start with PM2
pm2 start dist/index.js --name github-app
pm2 startup systemd
pm2 save

# Configure Nginx
sudo tee /etc/nginx/sites-available/github-app << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/github-app /etc/nginx/sites-enabled/
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx

echo "Setup complete!"
```

## Security Hardening

### Firewall (UFW)

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### Fail2ban

```bash
sudo apt install fail2ban

# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
```

### Secret Management

Options for managing secrets:

1. **HashiCorp Vault**
2. **AWS Secrets Manager** (even self-hosted can use)
3. **Encrypted environment files**
4. **Kubernetes Secrets** (with encryption at rest)

```typescript
// Using HashiCorp Vault
import Vault from "node-vault";

const vault = Vault({
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN,
});

async function getSecret(path: string): Promise<string> {
  const result = await vault.read(`secret/data/${path}`);
  return result.data.data.value;
}
```

## Monitoring

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
```

### Application Metrics

```typescript
// src/metrics.ts
import { collectDefaultMetrics, Registry, Counter, Histogram } from "prom-client";

const register = new Registry();
collectDefaultMetrics({ register });

export const webhookCounter = new Counter({
  name: "github_app_webhooks_total",
  help: "Total number of webhooks received",
  labelNames: ["event", "action"],
  registers: [register],
});

export const webhookDuration = new Histogram({
  name: "github_app_webhook_duration_seconds",
  help: "Webhook processing duration",
  labelNames: ["event"],
  registers: [register],
});

// Expose metrics endpoint
app.get("/metrics", async (req, res) => {
  res.set("Content-Type", register.contentType);
  res.end(await register.metrics());
});
```

## Logging

### Structured Logging

```typescript
// src/logger.ts
import pino from "pino";

export const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  transport:
    process.env.NODE_ENV === "development"
      ? { target: "pino-pretty" }
      : undefined,
});

// Usage
logger.info({ event: "pr_opened", pr: 123 }, "Processing PR");
```

### Log Aggregation

Options:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki + Grafana**
- **Fluentd**

## Backup Strategy

### Database Backups

```bash
#!/bin/bash
# /opt/scripts/backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/postgres

pg_dump -U github_app github_app | gzip > $BACKUP_DIR/github_app_$DATE.sql.gz

# Keep last 7 days
find $BACKUP_DIR -mtime +7 -delete

# Sync to S3 (optional)
aws s3 sync $BACKUP_DIR s3://your-bucket/backups/postgres/
```

```bash
# Cron: daily at 2 AM
0 2 * * * /opt/scripts/backup-db.sh
```

## High Availability

### Multi-Node Setup

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │   (HAProxy)     │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
   ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐
   │   App 1   │       │   App 2   │       │   App 3   │
   └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  PostgreSQL HA  │
                    │   (Patroni)     │
                    └─────────────────┘
```

## Production Checklist

- [ ] HTTPS configured with valid certificate
- [ ] Firewall rules configured
- [ ] Fail2ban or similar intrusion prevention
- [ ] Secrets stored securely (Vault, etc.)
- [ ] Database backups automated
- [ ] Log aggregation configured
- [ ] Monitoring and alerting set up
- [ ] Health checks configured
- [ ] Auto-restart on failure (PM2, systemd)
- [ ] Security updates automated
- [ ] Disaster recovery plan tested

## See Also

- [Hosting Overview](README.md)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
