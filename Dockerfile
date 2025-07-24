FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git-all \
    ffmpeg \
    libmagickwand-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY Bot/ ./Bot/
COPY .env .
COPY cookiebot-bucket-key.json .

WORKDIR /app/Bot

# Create healthcheck script
RUN echo '#!/bin/bash\n\
if pgrep -f "python.*COOKIEBOT.py" > /dev/null; then\n\
    exit 0\n\
else\n\
    exit 1\n\
fi' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh

# Add entrypoint script
RUN echo '#!/bin/bash\n\
BOT_ID=${BOT_ID:-0}\n\
echo "Starting COOKIEBOT instance $BOT_ID"\n\
exec python3.11 COOKIEBOT.py $BOT_ID' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

ENTRYPOINT ["/app/entrypoint.sh"]