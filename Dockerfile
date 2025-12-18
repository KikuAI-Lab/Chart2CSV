FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY api/requirements.txt ./api-requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r api-requirements.txt

# Copy application code
COPY chart2csv/ ./chart2csv/
COPY api/ ./api/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
