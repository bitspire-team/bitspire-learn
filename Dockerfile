FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install dependencies from pyproject.toml
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Expose port 8080 as configured in proxy.py
EXPOSE 8080

# Run the proxy application
CMD ["python", "proxy.py"]
