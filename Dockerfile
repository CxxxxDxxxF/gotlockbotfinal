# Use official Python image
FROM python:3.11-slim

# Use a non-root user
RUN useradd --create-home --shell /bin/bash botuser

# Set working dir & env
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system deps (incl. Tesseract) and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
         git \
         tesseract-ocr \
         libtesseract-dev \
         libleptonica-dev \
         pkg-config \
         poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip & install Python deps
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure tmp folder exists
RUN mkdir -p /app/tmp \
    && chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Default command
CMD ["python", "bot.py"]
