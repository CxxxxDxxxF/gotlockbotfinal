# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Start the bot (replace with your main filename if different)
CMD ["python", "main.py"]
