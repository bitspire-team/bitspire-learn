FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
RUN pip install --no-cache-dir uv && uv pip install --system --no-cache -r pyproject.toml

# Copy application source code
COPY src/ /app/src/

# Expose port 8080 as configured in settings
EXPOSE 8080

# Run the proxy application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
