# 🚀 VPS Deployment Guide - Instant Video Cover Bot

Complete step-by-step guide to deploy the bot on a VPS using Docker.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [VPS Setup](#vps-setup)
3. [Docker Deployment](#docker-deployment)
4. [Configuration](#configuration)
5. [Running the Bot](#running-the-bot)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### What You Need

- VPS with Ubuntu/Debian (2GB RAM minimum, 10GB disk)
- SSH access to your VPS
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- MongoDB Atlas account (free tier available)
- Your Telegram user ID

### Recommended VPS Providers

- DigitalOcean ($6/month)
- Linode ($5/month)
- Vultr ($3.50/month)
- AWS Free Tier
- Hetzner ($5/month)

---

## VPS Setup

### Step 1: Connect to VPS

```bash
# SSH into your VPS
ssh root@your_vps_ip

# Or with specific user
ssh username@your_vps_ip
```

### Step 2: Update System

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget nano
```

### Step 3: Install Docker

```bash
# Download Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh

# Run installer
sudo sh get-docker.sh

# Add your user to docker group (optional but recommended)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

### Step 4: Install Docker Compose

```bash
# Download latest Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

---

## Docker Deployment

### Step 1: Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/yourusername/video-cover-bot.git
cd video-cover-bot

# Or if you have SSH key setup
git clone git@github.com:yourusername/video-cover-bot.git
cd video-cover-bot
```

### Step 2: Setup Environment File

```bash
# Copy example file
cp ,env.example config.env

# Edit configuration
nano config.env
```

**Fill in the values:**

```ini
# Get from @BotFather in Telegram
BOT_TOKEN=your_bot_token_here

# Get from @userinfobot in Telegram
OWNER_ID=your_telegram_user_id

# Your force subscribe channel ID (with - prefix)
# To get: forward any message from channel to bot, check logs
FORCE_SUB_CHANNEL_ID=-1002659719637

# Log channel ID (where all bot actions are logged)
LOG_CHANNEL_ID=-1002659719637

# Home menu banner URL (optional, set if you have one)
HOME_MENU_BANNER_URL=https://example.com/banner.jpg

# Force subscribe banner URL (optional)
FORCE_SUB_BANNER_URL=https://example.com/fsub_banner.jpg

# MongoDB Atlas connection string
# Format: mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority

# Database name
MONGODB_DATABASE=video_cover_bot

# Optional: GitHub repo for auto-updates
UPSTREAM_REPO=https://github.com/yourusername/video-cover-bot
UPSTREAM_BRANCH=main
```

### Step 3: Setup Docker Compose File

```bash
# Check if docker-compose.yml exists
ls -la docker-compose.yml

# If not, create it
nano docker-compose.yml
```

**Paste this content:**

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: video-cover-bot
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      OWNER_ID: ${OWNER_ID}
      FORCE_SUB_CHANNEL_ID: ${FORCE_SUB_CHANNEL_ID}
      LOG_CHANNEL_ID: ${LOG_CHANNEL_ID}
      HOME_MENU_BANNER_URL: ${HOME_MENU_BANNER_URL}
      FORCE_SUB_BANNER_URL: ${FORCE_SUB_BANNER_URL}
      MONGODB_URI: ${MONGODB_URI}
      MONGODB_DATABASE: ${MONGODB_DATABASE}
      UPSTREAM_REPO: ${UPSTREAM_REPO}
      UPSTREAM_BRANCH: ${UPSTREAM_BRANCH}
    restart: unless-stopped
    networks:
      - bot-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  bot-network:
    driver: bridge
```

---

## Configuration

### MongoDB Setup

#### Option 1: MongoDB Atlas (Recommended)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free account
3. Create new cluster (M0 free tier)
4. Wait for cluster to be created (5-10 minutes)
5. Click "Connect"
6. Select "Connect Your Application"
7. Copy connection string
8. Replace username & password
9. Add to `config.env` as `MONGODB_URI`

**Example:**
```
mongodb+srv://admin:mypassword@cluster0.xxxxx.mongodb.net/video_cover_bot?retryWrites=true&w=majority
```

#### Option 2: Local MongoDB (Not Recommended for Production)

If you want to run MongoDB in Docker:

```yaml
# Add this to docker-compose.yml under services:
  mongo:
    image: mongo:latest
    container_name: mongo-db
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped
    networks:
      - bot-network
    ports:
      - "27017:27017"

volumes:
  mongo_data:
```

Then use: `mongodb://mongo:27017` as MONGODB_URI

### Telegram Channel Setup

1. **Create Force Subscribe Channel**
   - Open Telegram
   - Create new channel (private)
   - Add your bot as admin
   - Forward any message from channel to bot
   - Check bot logs for channel ID
   - Note: ID will have `-100` prefix, e.g., `-1002659719637`

2. **Create Log Channel**
   - Create another private channel
   - Add your bot as admin
   - Follow same process to get ID
   - Set as `LOG_CHANNEL_ID`

3. **Update config.env**
   ```ini
   FORCE_SUB_CHANNEL_ID=-1002659719637
   LOG_CHANNEL_ID=-1002659719637
   ```

---

## Running the Bot

### Step 1: Build and Start

```bash
# From the repo directory
cd ~/video-cover-bot

# Build Docker image and start containers
docker-compose up -d

# Check if containers are running
docker-compose ps

# Should show:
# NAME                  STATUS
# video-cover-bot       Up X seconds
```

### Step 2: Verify Bot is Working

```bash
# Check bot logs
docker-compose logs -f bot

# You should see:
# ✅ All handlers registered
# Bot starting (polling)
```

### Step 3: Test the Bot

1. Open Telegram
2. Find your bot
3. Send `/start`
4. Bot should respond with home menu

**Troubleshooting:**

```bash
# If bot doesn't respond, check logs
docker-compose logs bot

# Stop the bot
docker-compose down

# View detailed logs
docker-compose logs --tail=50 bot

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## Monitoring & Maintenance

### Check Bot Status

```bash
# See all containers
docker ps

# Check specific bot
docker ps | grep video-cover-bot

# View real-time logs
docker-compose logs -f bot

# View last 100 lines
docker-compose logs --tail=100 bot
```

### Restart Bot

```bash
# Restart service
docker-compose restart bot

# Full restart
docker-compose down
docker-compose up -d
```

### Update Code

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs -f bot
```

### Backup Database

```bash
# If using MongoDB Atlas, automatic backups available
# If using local MongoDB:

docker exec mongo-db mongodump --out /backup
docker cp mongo-db:/backup ./mongo-backup
```

### View Space Usage

```bash
# Docker space usage
docker system df

# Clean up unused images/containers
docker system prune -a

# Check VPS disk
df -h
```

---

## Advanced Configuration

### Enable Auto-Updates

Edit `config.env`:

```ini
UPSTREAM_REPO=https://github.com/yourusername/video-cover-bot
UPSTREAM_BRANCH=main
```

Then in Telegram (as admin):
```
/restart
```

Bot will pull latest changes automatically.

### Custom Banners

1. Upload banner images to your server:
   ```bash
   # Upload via SCP or SFTP
   scp banner.jpg user@vps_ip:~/video-cover-bot/ui/
   ```

2. Update `config.env`:
   ```ini
   HOME_MENU_BANNER_URL=https://yourdomain.com/banners/home.jpg
   FORCE_SUB_BANNER_URL=https://yourdomain.com/banners/fsub.jpg
   ```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  bot:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Port Forwarding (If Needed)

```yaml
services:
  bot:
    ports:
      - "8080:8080"  # If bot exposes any HTTP port
```

---

## Troubleshooting

### Bot Crashes

```bash
# Check error logs
docker-compose logs bot

# Common issues:
# - Invalid BOT_TOKEN
# - MongoDB connection error
# - Channel ID format wrong

# Fix and restart
docker-compose restart bot
```

### MongoDB Connection Failed

```bash
# Verify credentials
echo $MONGODB_URI

# Test connection
docker exec video-cover-bot python -c "from pymongo import MongoClient; MongoClient('mongodb+srv://...')"

# If using local MongoDB
docker-compose logs mongo
```

### Bot Not Responding in Telegram

1. Verify bot token: `/start` in Telegram
2. Check logs: `docker-compose logs bot`
3. Ensure bot admin in channels
4. Restart: `docker-compose restart bot`

### Out of Disk Space

```bash
# Check usage
df -h

# Clean old Docker data
docker system prune -a

# Remove old logs
docker-compose logs --tail=10 > /dev/null

# If still low, increase VPS disk or upgrade
```

---

## Performance Tuning

### For High Load

1. **Increase Memory**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

2. **Use MongoDB Indexes**
   ```bash
   docker exec mongo-db mongosh
   > db.users.createIndex({user_id: 1})
   > db.banned_users.createIndex({user_id: 1})
   ```

3. **Monitor Resources**
   ```bash
   docker stats
   ```

---

## Backup & Recovery

### Automated Backups

```bash
# Create backup script
nano ~/video-cover-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="$HOME/bot-backups"
mkdir -p $BACKUP_DIR

# Backup config
cp ~/video-cover-bot/config.env $BACKUP_DIR/config.env.$(date +%Y%m%d)

# Backup database (if local MongoDB)
docker exec mongo-db mongodump --out /backup
docker cp mongo-db:/backup $BACKUP_DIR/mongo-$(date +%Y%m%d)

# Keep only last 7 backups
find $BACKUP_DIR -mtime +7 -delete
```

```bash
# Make executable
chmod +x ~/video-cover-backup.sh

# Add to crontab for daily backups
crontab -e
# Add line: 0 2 * * * ~/video-cover-backup.sh
```

---

## Security Best Practices

1. **Keep config.env Secret**
   ```bash
   chmod 600 config.env
   ```

2. **Use Environment Variables**
   - Never commit config.env to git
   - Add to .gitignore

3. **Regular Updates**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **Firewall Rules**
   ```bash
   sudo ufw allow 22/tcp      # SSH
   sudo ufw allow 80/tcp      # HTTP (if needed)
   sudo ufw allow 443/tcp     # HTTPS (if needed)
   sudo ufw enable
   ```

---

## Quick Reference

```bash
# Start bot
docker-compose up -d

# Stop bot
docker-compose down

# View logs
docker-compose logs -f bot

# Restart
docker-compose restart bot

# Rebuild
docker-compose up -d --build

# Update code
git pull && docker-compose up -d --build

# Check status
docker-compose ps
docker stats

# See all commands
docker-compose help
```

---

## Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs bot`
2. Verify config.env
3. Check MongoDB connection
4. Ensure Telegram channels are set correctly
5. Create GitHub issue with error details

---

<div align="center">

**🎉 Your bot should now be running on your VPS!**

Need help? Check the main [README.md](README.md)

</div>
