FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY WHR2023.csv .

# Set environment variables for Shiny
ENV SHINY_HOST=0.0.0.0
ENV SHINY_PORT=7860

# Expose port
EXPOSE 7860

# Run the app
CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
