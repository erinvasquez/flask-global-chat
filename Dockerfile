# Preparing for Cloud Run
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libdbus-1-dev \
    libglib2.0-dev \
    libcurl4-openssl-dev \
    pkg-config \
    meson \
    libssl-dev \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080

# Local testing only, cloud run $port must come from the environment
#CMD ["sh", "-c", "gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 wsgi:app"]
# Changing from JSOn array to string (shell form)
CMD gunicorn --bind ":${PORT}" --workers 1 --threads 8 --timeout 0 wsgi:app