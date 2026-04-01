FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgeos-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-vie \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# pylzma fails to compile on Linux (ARM/aarch64) with newer GCC – it is a
# 7-zip wrapper that is not required by the Rawiq RAG pipeline, so we drop it.
RUN pip install --upgrade pip && \
    grep -v "^pylzma" requirements.txt | pip install -r /dev/stdin

# Copy project source code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Default command: run Streamlit frontend
CMD ["streamlit", "run", "frontend/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
