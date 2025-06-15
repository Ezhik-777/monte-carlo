# Monte Carlo Investment Calculator - Docker Configuration

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements-advanced.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-advanced.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Create non-root user for security
RUN groupadd -r monte && useradd -r -g monte monte
RUN chown -R monte:monte /app
USER monte

# Start application
CMD ["python", "run.py"]