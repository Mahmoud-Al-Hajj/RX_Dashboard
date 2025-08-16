# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Switch to non-root user
USER app

# Create startup script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'export PYTHONPATH=/app/src' >> /app/start.sh && \
    echo 'if [ "$1" = "api" ]; then' >> /app/start.sh && \
    echo '    exec python main.py api' >> /app/start.sh && \
    echo 'elif [ "$1" = "dashboard" ]; then' >> /app/start.sh && \
    echo '    exec streamlit run src/dashboard/main.py --server.port 8501 --server.address 0.0.0.0' >> /app/start.sh && \
    echo 'else' >> /app/start.sh && \
    echo '    echo "Usage: docker run remotelyx-dashboard [api|dashboard]"' >> /app/start.sh && \
    echo '    exit 1' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default command
CMD ["/app/start.sh", "api"] 