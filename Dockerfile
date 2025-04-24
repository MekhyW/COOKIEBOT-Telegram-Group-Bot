FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git-all \
    ffmpeg \
    libmagickwand-dev \
    screen \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Bot/ ./Bot/
COPY .env .
COPY cookiebot-bucket-key.json .
COPY nginx.conf .

WORKDIR /app/Bot

RUN echo '#!/bin/bash\n\
for i in {0..4}; do\n\
    screen -dmS bot$i python3.11 COOKIEBOT.py $i\n\
done\n\
# Keep container running\n\
tail -f /dev/null' > start.sh && \
    chmod +x start.sh

CMD ["./start.sh"]