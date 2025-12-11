# ==========================================
# Stage 1: Base Development
# ==========================================
FROM python:3.10-slim as development

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY . .

# Create sessions directory with proper permissions
RUN mkdir -p /app/sessions && \
    chown -R appuser:appuser /app/sessions

# Copy and set permissions for entrypoint
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod 755 /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# ==========================================
# Stage 2: Production
# ==========================================
FROM python:3.10-slim as production

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from development stage
COPY --from=development /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=development /usr/local/bin /usr/local/bin

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create sessions directory
RUN mkdir -p /app/sessions && \
    chown -R appuser:appuser /app/sessions

# Copy and set permissions for entrypoint
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod 755 /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Production command (no reload, single worker since we have K8s replicas)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
