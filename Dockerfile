FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for database and data
RUN mkdir -p /app/instance /app/data

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]