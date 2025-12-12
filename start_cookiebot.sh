#!/bin/bash

cd /home/YOUR_USER/COOKIEBOT-Telegram-Group-Bot/Bot

for i in {0..4}
do
    screen -dmS cookiebot_$i bash -c "python3.11 LAUNCHER.py $i"
done
