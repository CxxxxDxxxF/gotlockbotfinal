# Dockerfile

FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash botuser

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system deps (Tesseract, tzdata for zoneinfo, etc.)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       git \
       tesseract-ocr \
       libtesseract-dev \
       libleptonica-dev \
       pkg-config \
       poppler-utils \
       tzdata \
  && rm -rf /var/lib/apt/lists/*

# Copy & install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy source & set permissions
COPY . .
RUN mkdir -p tmp \
    && chown -R botuser:botuser /app

USER botuser

# Start bot
ENTRYPOINT ["bash", "run.sh"]

