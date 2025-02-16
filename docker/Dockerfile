FROM python:3.11-slim

# Set build args for cache control
ARG CACHEBUST=1

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nodejs \
    npm \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g prettier@3.4.2

# Set working directory
WORKDIR /app

# Handle Python dependencies in one layer
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source and setup environment in one layer
COPY src/ ./src/
RUN mkdir -p /data && chmod 777 /data

# Environment configuration
ENV PYTHONPATH=/app \
    DATA_DIR=/data

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]