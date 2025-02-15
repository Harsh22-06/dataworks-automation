FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    git curl nodejs npm ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g prettier@3.4.2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]