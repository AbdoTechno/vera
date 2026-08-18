# ==========================================
# VERA Clinical Intelligence Platform - Dockerfile
# ==========================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    ENV=production \
    HOME=/home/user

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for Hugging Face Spaces & security
RUN useradd -m -u 1000 user
WORKDIR $HOME/app

# Install python dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and data
COPY --chown=user:user . $HOME/app

USER user
EXPOSE 7860 8000

CMD ["python", "run_server.py"]

