# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies (e.g., tesseract-ocr for OCR, build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up user for Hugging Face Spaces compatibility (uid 1000)
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install python dependencies
COPY --chown=user:user requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt

# Copy source code with proper permissions
COPY --chown=user:user . $HOME/app

USER user

# Hugging Face Spaces defaults to 7860
ENV PORT=7860
EXPOSE 7860

# Run FastAPI with Uvicorn (uses $PORT if provided, fallback to 7860)
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
