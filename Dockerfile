# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /code

# Install system dependencies (including Playwright browser deps)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        # Playwright dependencies
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libdbus-1-3 \
        libxkbcommon0 \
        libatspi2.0-0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libpango-1.0-0 \
        libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python dependency installs
ENV UV_LINK_MODE=copy
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# uv installs to ~/.local/bin by default; ensure it's on PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy pyproject.toml and install Python dependencies via uv
COPY pyproject.toml .
RUN uv pip install --system --no-cache -e .

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY main.py .

# Run the application
ENTRYPOINT ["python"]
CMD ["main.py"]
