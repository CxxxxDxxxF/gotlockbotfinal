# Dockerfile

FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash botuser

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install only what's needed for HTTPS & OCR
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       ca-certificates \
       tesseract-ocr \
       libtesseract-dev \
       libleptonica-dev \
       pkg-config \
       poppler-utils \
       tzdata \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy source & fix permissions
COPY . .
RUN mkdir -p tmp \
    && chown -R botuser:botuser /app

USER botuser

ENTRYPOINT ["bash", "run.sh"]
