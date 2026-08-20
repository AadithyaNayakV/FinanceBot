# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies (e.g., tesseract-ocr for OCR, build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
