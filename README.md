# COOKIEBOT-Telegram-Group-Bot

Telegram chatbot responsible for protecting chats against spammers, conversating using natural language, perform speech-to-text, search media, schedule posts and provides fun features for events.

## Installation on Ubuntu

```bash
sudo apt update
sudo apt-get install git-all
sudo apt install python3.11
sudo apt install python3-pip
sudo apt install ffmpeg
sudo apt-get install libmagickwand-dev
sudo apt-get install screen
git clone https://github.com/MekhyW/COOKIEBOT-Telegram-Group-Bot.git
cd COOKIEBOT-Telegram-Group-Bot
pip3 install -r requirements.txt --break-system-packages
cd ..
git clone https://github.com/MekhyW/telepota.git
cd telepota
pip3 install . --break-system-packages
```

## Provide credentials

```bash
nano .env # Add your credentials
```

## Set timezone

```bash
timedatectl list-timezones
sudo timedatectl set-timezone <your_time_zone>
timedatectl
```

## Run the bot

```bash
screen
python3.11 LAUNCHER.py [isBombot] # Run with process monitoring
python3.11 COOKIEBOT.py [isBombot] # Run without process monitoring
# Press CTRL+A+D to detach from the screen
```