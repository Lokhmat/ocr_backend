FROM python:3.10-slim

# System deps
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --no-cache-dir \
    torch torchvision torchaudio \
    transformers accelerate \
    fastapi uvicorn

# Copy app code
COPY . /app
WORKDIR /app

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
