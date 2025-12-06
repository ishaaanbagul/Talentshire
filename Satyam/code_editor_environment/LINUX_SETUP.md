# Linux Setup Guide (Option B) - Recommended for Production

This guide walks you through deploying CodePlay on a Linux host where Piston will work properly with full isolation.

---

## Step 1: Prepare Linux Host

You have 3 choices:

### Choice 1: Ubuntu Server (Physical/Cloud)
- AWS EC2 (Ubuntu 22.04 LTS, t3.medium or larger)
- DigitalOcean (Ubuntu 22.04, $6/month Basic)
- Azure VM (Ubuntu 22.04)
- Your own Linux server

### Choice 2: VirtualBox VM (On Windows)
```bash
# Download Ubuntu 22.04 LTS Server ISO
# Create VM with 4GB RAM, 20GB disk
# Install Ubuntu in VM
```

### Choice 3: Hyper-V VM (On Windows)
```powershell
# Create Ubuntu Gen 2 VM on Hyper-V
# 4GB RAM, 20GB disk
# Install Ubuntu 22.04 LTS Server
```

---

## Step 2: Install Docker & Docker Compose on Linux

SSH into your Linux host and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose git

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, avoids sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

Verify Docker is working:
```bash
docker --version
docker compose version
```

---

## Step 3: Clone/Deploy CodePlay

```bash
# Clone the repository
cd /opt
git clone <your-repo-url> codeplay
cd codeplay

# OR copy files manually via SCP/rsync
# scp -r ./new_project user@linux-host:/opt/codeplay
```

Verify files:
```bash
ls -la
# Should see: backend/ frontend/ docker-compose.yml README.md etc.
```

---

## Step 4: Start the Application

```bash
# Build and start all services
docker compose up --build -d

# Wait 15 seconds for services to initialize
sleep 15

# Check status
docker compose ps
# All containers should show "Up"

# Check Piston health
docker compose logs piston | tail -20
# Should see: "[INFO] API server listening on 0.0.0.0:8080"
```

---

## Step 5: Access the Application

Get your Linux server IP:
```bash
hostname -I
# Example output: 192.168.1.100
```

Open browser on any machine:
```
http://192.168.1.100:3000
```

**Test it:**
1. Write Python code: `print(3 + 5)`
2. Click "Run"
3. See output: `8`

---

## Step 6: Test with Java

Write Java code:
```java
class Main {
  public static void main(String[] args) {
    System.out.println("3 + 5 = " + (3 + 5));
  }
}
```

Select language: Java
Click "Run"
Should output: `3 + 5 = 8`

---

## Step 7: Monitor & Maintain

### Check Piston Status
```bash
curl http://localhost:8080/api/v2/runtimes | jq '. | length'
# Should return: 40+ languages
```

### View Live Logs
```bash
docker compose logs -f
# Or for specific service:
docker compose logs -f piston
docker compose logs -f codeplay-backend
```

### Restart Services
```bash
docker compose restart
# Or specific service:
docker compose restart piston
```

### Stop All
```bash
docker compose stop
```

### Rebuild After Code Changes
```bash
docker compose down
docker compose up --build -d
```

---

## Step 8: Firewall (If Needed)

If using cloud provider (AWS, DigitalOcean, Azure):

**Allow inbound traffic on port 3000:**

### AWS Security Group
- Inbound Rule: TCP port 3000 from anywhere (0.0.0.0/0)

### DigitalOcean Firewall
- Allow: HTTP (80) and Custom (3000)

### Azure NSG
- Inbound Rule: TCP 3000 from any source

---

## Troubleshooting on Linux

### Issue: "Cannot connect to Piston"
```bash
# Check if Piston is running
docker compose ps

# View Piston logs
docker compose logs piston

# Restart Piston
docker compose restart piston

# Wait 10 seconds
sleep 10

# Test Piston API
curl http://localhost:8080/api/v2/runtimes
```

### Issue: "Port 3000 already in use"
```bash
# Edit docker-compose.yml
# Change: "3000:80" to "3001:80"
# Then restart

docker compose down
docker compose up --build -d
```

### Issue: "Out of disk space"
```bash
# Clean up Docker
docker system prune -a

# Check disk usage
df -h
```

---

## Performance Tips

### For VPS/Small Instances (1GB RAM)
```yaml
# In docker-compose.yml, add to piston service:
environment:
  - PISTON_MAX_COMPILE_TIME=30
  - PISTON_MAX_RUN_TIME=10
deploy:
  resources:
    limits:
      memory: 512M
```

### For Scaling (Multiple Piston Instances)
```bash
# Start 3 Piston instances
docker compose up -d --scale piston=3

# Note: You'll need a load balancer in backend (future enhancement)
```

---

## Production Checklist

- [ ] Set up Linux host (AWS/DigitalOcean/etc.)
- [ ] Install Docker & Docker Compose
- [ ] Deploy CodePlay code
- [ ] Run `docker compose up --build -d`
- [ ] Test at http://server-ip:3000
- [ ] Configure firewall (allow port 3000)
- [ ] Set up SSL/HTTPS (use Nginx reverse proxy with Let's Encrypt)
- [ ] Enable auto-restart: `docker compose up -d --no-recreate`
- [ ] Set up monitoring/logs (optional)
- [ ] Configure CI/CD for auto-deployment (optional)

---

## SSL/HTTPS Setup (Optional but Recommended)

Use Nginx as reverse proxy with Let's Encrypt:

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (replace example.com with your domain)
sudo certbot certonly --standalone -d example.com

# Create Nginx config to proxy to localhost:3000
# Configure Nginx to use the certificate
# Restart Nginx

# Users access: https://example.com instead of http://ip:3000
```

---

## Next Steps

1. **Database:** Connect MongoDB for persistent problem storage
2. **Code Generation:** Add a service to generate problems dynamically
3. **Microservices:** Split into separate services (Question, Execution, API Gateway)
4. **CI/CD:** Set up GitHub Actions to auto-deploy on push
5. **Monitoring:** Add health checks, error tracking, performance monitoring

See main README.md for architecture details.
