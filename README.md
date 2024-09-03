# COOKIEBOT-Telegram-Group-Bot

Telegram chatbot responsible for protecting chats against spammers, conversating using natural language, perform speech-to-text, search media, schedule posts and provides fun features for events.

## Installation on Ubuntu

```bash
sudo apt update -y
sudo apt-get install git-all -y
sudo apt install python3.11 -y
sudo apt install python3-pip -y
sudo apt install ffmpeg -y
sudo apt-get install libmagickwand-dev -y
sudo apt-get install screen -y
sudo apt install fail2ban -y
git clone https://github.com/MekhyW/COOKIEBOT-Telegram-Group-Bot.git
cd COOKIEBOT-Telegram-Group-Bot
pip3 install -r requirements.txt --break-system-packages
cd ..
```

## Provide credentials

```bash
cd COOKIEBOT-Telegram-Group-Bot
nano .env # Add your credentials
nano cookiebot-bucket-key.json # Add your credentials
```

## Set timezone

```bash
timedatectl list-timezones
sudo timedatectl set-timezone <your_time_zone>
timedatectl
```

## Run the bot

```bash
cd Bot
screen
python3.11 LAUNCHER.py [is_alternate_bot (int)] # Run with process monitoring
python3.11 COOKIEBOT.py [is_alternate_bot (int)] # Run without process monitoring
# Press CTRL+A+D to detach from the screen
```
