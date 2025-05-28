FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd -r ddns && useradd -r -g ddns ddns

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Change ownership to non-root user
RUN chown -R ddns:ddns /app

# Switch to non-root user
USER ddns

# Run the application with unbuffered output
CMD ["python", "-u", "main.py"]