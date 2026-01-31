# Enterprise Automation Framework - Docker Image

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy framework code
COPY config/ ./config/
COPY framework/ ./framework/
COPY tests/ ./tests/
COPY utils/ ./utils/
COPY pages/ ./pages/
COPY pytest.ini .
COPY setup.py .

# Create necessary directories
RUN mkdir -p logs screenshots videos traces reports allure-results

# Set environment variables
ENV PYTHONPATH=/app
ENV TEST_ENV=dev

# Default command
CMD ["pytest", "--headless", "-v", "--alluredir=allure-results"]
