# Dockerfile

# 1) Base image
FROM python:3.11-slim

# 2) Create non-root user
RUN useradd --create-home --shell /bin/bash botuser

# 3) Set working directory & env
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# 4) Install system deps (git+certs for GitHub pip, Tesseract, tzdata)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       git \
       && apt-get install -y --no-install-recommends \
       ca-certificates \
       tesseract-ocr \
       libtesseract-dev \
       libleptonica-dev \
       pkg-config \
       poppler-utils \
       tzdata \
  && rm -rf /var/lib/apt/lists/*

# 5) Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 6) Copy source & set permissions
COPY . .
RUN mkdir -p tmp \
    && chown -R botuser:botuser /app

# 7) Switch to non-root user
USER botuser

# 8) Entrypoint
ENTRYPOINT ["bash", "run.sh"]
