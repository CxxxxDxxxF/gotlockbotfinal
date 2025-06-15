# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git tesseract-ocr libtesseract-dev libleptonica-dev pkg-config poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables from .env file (optional, if you use Docker secrets instead skip this)
ENV PYTHONUNBUFFERED=1

# Run bot
CMD ["python", "bot.py"]
