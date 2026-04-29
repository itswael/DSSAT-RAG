# Deployment Guide

Complete instructions for deploying the DSSAT RAG Chatbot Frontend to various platforms.

## Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All tests pass: `npm test`
- [ ] No type errors: `npm run type-check`
- [ ] No linting errors: `npm run lint`
- [ ] Build succeeds: `npm run build`
- [ ] Environment variables configured
- [ ] n8n service is accessible from deployment location
- [ ] SSL/HTTPS is configured
- [ ] API base URL is correct for production

## Deployment Options

### Option 1: Vercel (Recommended)

**Advantages**:
- Native Next.js support
- Zero-config deployment
- Automatic preview deployments
- CDN included
- Free tier available

**Setup**:

1. **Push to GitHub**:
```bash
git add .
git commit -m "ready for deployment"
git push origin main
```

2. **Create Vercel Account**:
   - Visit https://vercel.com
   - Sign up with GitHub

3. **Import Project**:
   - Click "Add New..." → "Project"
   - Select your repository
   - Click "Import"

4. **Configure Environment**:
   - Go to Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_BASE_URL`: Your production n8n URL
   - Example: `https://n8n.yourdomain.com`

5. **Deploy**:
   - Vercel will auto-deploy on push to main
   - Preview deployments on pull requests

6. **Access**:
   - Default domain: `https://project-name.vercel.app`
   - Or use custom domain in settings

### Option 2: Docker + Any Server

**Advantages**:
- Full control over environment
- Deploy anywhere
- Easy updates

**Requirements**:
- Docker installed on server
- Access to your server (SSH)

**Steps**:

1. **Build Docker Image**:
```bash
# Build locally first
docker build -t dssat-chatbot-ui:latest .

# Test locally
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:5678 \
  dssat-chatbot-ui:latest
```

2. **Push to Registry** (DockerHub or private):
```bash
# Login to DockerHub
docker login

# Tag image
docker tag dssat-chatbot-ui:latest your-username/dssat-chatbot-ui:latest

# Push
docker push your-username/dssat-chatbot-ui:latest
```

3. **Deploy to Server**:
```bash
# SSH into server
ssh user@your-server.com

# Pull image
docker pull your-username/dssat-chatbot-ui:latest

# Run container
docker run -d \
  --name dssat-chatbot \
  --restart always \
  -p 80:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=https://n8n.yourdomain.com \
  your-username/dssat-chatbot-ui:latest

# Verify
docker logs dssat-chatbot
```

### Option 3: AWS Amplify

**Advantages**:
- AWS ecosystem integration
- Easy CI/CD setup
- Multiple environment support

**Steps**:

1. **Connect Repository**:
   - AWS Amplify → New App → Host web app
   - Select GitHub provider
   - Authorize GitHub

2. **Configure Build**:
   - Framework: Next.js
   - Build settings auto-detected

3. **Environment Variables**:
   - Add `NEXT_PUBLIC_API_BASE_URL` in console

4. **Deploy**:
   - Amplify auto-deploys on push
   - Check deployment logs

### Option 4: Railway

**Advantages**:
- Simple deployment
- Free tier with GitHub
- Built-in environment variables

**Steps**:

1. **Connect GitHub**:
   - Go to https://railway.app
   - Create account → Connect GitHub

2. **Create Project**:
   - New Project → GitHub Repo
   - Select your repository

3. **Configure**:
   - Add environment variable: `NEXT_PUBLIC_API_BASE_URL`
   - Railway auto-detects Next.js

4. **Deploy**:
   - Automatic deployment starts
   - View logs in dashboard

### Option 5: Self-Hosted (Ubuntu Server)

**Requirements**:
- Ubuntu 20.04+ server
- Node.js 18+
- Nginx or Apache
- PM2 or similar process manager

**Setup**:

1. **SSH into Server**:
```bash
ssh user@your-server.com
```

2. **Install Dependencies**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
sudo npm install -g pm2
```

3. **Clone and Setup**:
```bash
# Clone repository
git clone <your-repo-url> /var/www/dssat-chatbot
cd /var/www/dssat-chatbot

# Install dependencies
npm install --production

# Build
npm run build

# Create environment file
echo 'NEXT_PUBLIC_API_BASE_URL=https://n8n.yourdomain.com' > .env.production
```

4. **Start with PM2**:
```bash
# Start app
pm2 start npm --name "dssat-chatbot" -- start

# Make startup script
pm2 startup
pm2 save

# Check status
pm2 status
```

5. **Configure Nginx**:
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/dssat-chatbot
```

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
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dssat-chatbot \
  /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

6. **Setup SSL with Let's Encrypt**:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Update Nginx config to use SSL
# (Certbot can auto-configure with --nginx flag)
```

## Post-Deployment

### Monitoring

**Application Health**:
```bash
# Check application is running
curl https://yourdomain.com

# Should return HTML home page
```

**Error Monitoring**:
- Vercel: Automatic error tracking
- Docker/Self-hosted: Set up Sentry or similar
- All platforms: Check browser console for errors

### Logging

**Vercel**:
- View logs in Deployment page
- Check Runtime Logs tab

**Docker/PM2**:
```bash
# View logs
docker logs dssat-chatbot
# or
pm2 logs dssat-chatbot

# View in real-time
pm2 logs dssat-chatbot --lines 100 --raw
```

### Updates & Maintenance

**Update Application**:

For Vercel/AWS:
```bash
git commit -m "update: improvements"
git push origin main
# Auto-deploys
```

For Docker/Self-hosted:
```bash
# Pull latest code
git pull origin main

# Build new image
docker build -t dssat-chatbot-ui:v2 .

# Deploy new version
docker stop dssat-chatbot
docker rm dssat-chatbot
docker run -d \
  --name dssat-chatbot \
  -p 80:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=https://n8n.yourdomain.com \
  dssat-chatbot-ui:v2
```

## SSL/HTTPS Setup

### Vercel
- Automatic SSL included
- Custom domain configuration in dashboard

### Self-hosted with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (auto-renew)
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal (check status)
sudo systemctl status certbot.timer
```

## Performance Optimization

### Build Optimization
```bash
# Analyze bundle size
npm run build

# Check .next/static/chunks for large files
# Consider code splitting for large components
```

### CDN Configuration

**Vercel**: Automatic
- Served from nearest edge location
- Image optimization included

**Self-hosted**:
```bash
# Use Cloudflare
# 1. Add domain to Cloudflare
# 2. Update DNS records
# 3. Enable caching in Cloudflare dashboard
```

### Image Optimization

```typescript
// Use Next.js Image component (if needed)
import Image from 'next/image'

<Image
  src="/path/to/image.jpg"
  alt="Description"
  width={800}
  height={600}
/>
```

## Scaling

### Single Server
- Works up to ~10k concurrent users
- Suitable for internal tools
- Monitored with PM2

### Horizontal Scaling
For higher traffic:

1. **Multiple Server Instances**:
   - Run app on multiple servers
   - Use load balancer (Nginx, HAProxy)
   - Share session data if needed

2. **Containerization**:
   - Kubernetes for orchestration
   - Docker Swarm for smaller deployments
   - Automatic scaling based on metrics

3. **Database**:
   - Store chat history if needed
   - Use PostgreSQL, MongoDB
   - Implement session management

## Troubleshooting Deployment

### App Not Starting
```bash
# Check logs
docker logs dssat-chatbot
pm2 logs dssat-chatbot

# Check environment variables
env | grep NEXT_PUBLIC

# Verify n8n connectivity
curl https://n8n.yourdomain.com/webhook/chat
```

### API Connection Fails
```bash
# Verify API URL
echo $NEXT_PUBLIC_API_BASE_URL

# Test connectivity
curl -X POST $NEXT_PUBLIC_API_BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"userQuery": "test"}'

# Check firewall rules
sudo ufw status
```

### High Memory Usage
```bash
# Check running processes
ps aux | grep node

# Restart application
pm2 restart dssat-chatbot
# or
docker restart dssat-chatbot
```

### Slow Performance
```bash
# Check server resources
htop
# Look for CPU/Memory bottlenecks

# Check n8n response time
curl -w "@curl-format.txt" -o /dev/null -s https://n8n.yourdomain.com

# Check application metrics
npm run build && npm start
```

## Rollback Procedure

### Vercel
- Go to Deployments
- Click on previous deployment
- Select "Promote to Production"

### Docker/PM2
```bash
# Save old image before updating
docker tag dssat-chatbot-ui:latest dssat-chatbot-ui:v1-backup

# If update fails, revert
docker run -d \
  --name dssat-chatbot \
  -p 80:3000 \
  dssat-chatbot-ui:v1-backup

# With PM2
pm2 revert
```

## Cost Optimization

### Vercel
- Free tier: Up to 100 deployments/month
- Paid: Starting at $15/month

### AWS Amplify
- Free tier: Up to 1000 build minutes/month
- Compute: On-demand pricing

### Self-hosted
- VPS: $3-10/month (DigitalOcean, Linode)
- Domain: $10/year
- SSL: Free (Let's Encrypt)

## Security Checklist

- [ ] HTTPS/SSL configured
- [ ] Environment variables secured (not in code)
- [ ] API key hidden (if used)
- [ ] Firewall rules configured
- [ ] Regular backups enabled
- [ ] Monitoring alerts set up
- [ ] Log aggregation enabled
- [ ] Regular security updates

## Monitoring & Alerts

**Key Metrics**:
- Response time (< 2 seconds)
- Error rate (< 1%)
- Uptime (99.9%)
- CPU usage (< 80%)
- Memory usage (< 80%)
- API connectivity

**Setup Alerts**:
- High error rate
- Application down
- High response time
- Resource limits exceeded

---

**Deployment successful? You're all set! 🎉**
