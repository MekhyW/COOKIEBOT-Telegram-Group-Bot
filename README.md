# COOKIEBOT-Telegram-Group-Bot

Telegram chatbot responsible for protecting chats against spammers, conversating using natural language, perform speech-to-text, search media, schedule posts and provides fun features for events.

Backend: https://github.com/MekhyW/COOKIEBOT-backend
Web: https://github.com/MekhyW/COOKIEBOT-WebHub

## Installation on Ubuntu

```bash
sudo apt update -y
sudo apt-get install git-all -y
sudo apt install python3.11 -y
sudo apt install python3-pip -y
sudo apt install ffmpeg -y
sudo apt-get install imagemagick libmagickwand-dev -y
sudo apt-get install screen -y
sudo apt install fail2ban -y
git clone https://github.com/MekhyW/COOKIEBOT-Telegram-Group-Bot.git
cd COOKIEBOT-Telegram-Group-Bot
pip3 install -r requirements.txt --break-system-packages
cd ..
```

## Setup nginx for JWT API

```bash
sudo apt-get install nginx -y
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot --nginx -d botserver.cookiebotfur.net
sudo ln -sf /home/YOUR_GMAIL/COOKIEBOT-Telegram-Group-Bot/nginx.conf /etc/nginx/nginx.conf
sudo systemctl restart nginx
```

## Provide credentials

```bash
cd COOKIEBOT-Telegram-Group-Bot
nano .env # Add your credentials
nano cookiebot-bucket-key.json # Add your credentials
cd ..
```

## Set timezone

```bash
timedatectl list-timezones
sudo timedatectl set-timezone <your_time_zone>
timedatectl
```

## Run the bot

### Option 1: Docker Deployment (Recommended)

Docker deployment provides better resource management and automatic recovery with 5 bot instances running in separate containers.

#### Install Docker Engine

```bash
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### Quick Start

```bash
./deploy.sh start     # Start all containers
./deploy.sh status    # Check status
./deploy.sh logs      # View logs
./deploy.sh stop      # Stop all containers
```

#### Monitoring

For advanced monitoring with automatic restart on resource exhaustion:

```bash
pip install docker # Install monitoring dependencies
python monitor.py # Start monitoring
python monitor.py --cpu-threshold 70 --memory-threshold 85 # Custom thresholds
```

#### Troubleshooting

```bash
docker logs cookiebot-instance-0 # Check container logs
docker stats # Check resource usage
./deploy.sh restart-service cookiebot-0 # Restart specific container
docker exec -it cookiebot-instance-0 /bin/bash # Enter container for debugging
```

### Option 2: Traditional Deployment

Traditional deployment runs the bot in the background using screen. It's more resource-intensive and unstable but doesn't require Docker.

```bash
cd Bot
screen
python3.11 LAUNCHER.py [is_alternate_bot (int)] # Run with process monitoring
python3.11 COOKIEBOT.py [is_alternate_bot (int)] # Run without process monitoring
# Press CTRL+A+D to detach from the screen
```

