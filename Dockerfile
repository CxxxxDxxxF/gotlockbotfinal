# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install system packages required for some Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Start the bot (replace with your main filename if different)
# Start the Discord bot
CMD ["python", "bot.py"]
