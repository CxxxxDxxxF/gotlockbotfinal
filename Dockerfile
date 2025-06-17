# ─── Dockerfile ───

# 1) Base image
FROM python:3.11-slim

# 2) Create non-root user
RUN useradd --create-home --shell /bin/bash botuser

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# 3) Install system deps (git+certs for GitHub pip, Tesseract, tzdata)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       git \
       ca-certificates \
       tesseract-ocr \
       libtesseract-dev \
       libleptonica-dev \
       pkg-config \
       poppler-utils \
       tzdata \
  && rm -rf /var/lib/apt/lists/*

# 4) Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 5) Copy code & adjust permissions
COPY . .
RUN mkdir -p tmp \
    && chown -R botuser:botuser /app

# 6) Switch to non-root
USER botuser

# 7) Entrypoint
ENTRYPOINT ["bash", "run.sh"]
