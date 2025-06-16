# Use official Python image
FROM python:3.11-slim

# Create a non-root user
RUN useradd --create-home --shell /bin/bash botuser

# Set working dir & env
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system deps (incl. Tesseract) and clean up
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
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

# Ensure tmp folder exists and chown everything to botuser
RUN mkdir -p /app/tmp \
    && chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Use your run script (it loads .env, creates tmp, then execs main.py)
ENTRYPOINT ["bash", "run.sh"]
