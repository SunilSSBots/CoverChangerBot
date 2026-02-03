FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (git REQUIRED for updater)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app

# Create non-root user
RUN useradd -m botuser || true
USER botuser

# Default command
CMD ["python", "bot.py"]