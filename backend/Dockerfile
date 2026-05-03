FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files into a 'backend' directory to preserve the package structure
COPY . backend/

# Use the PORT environment variable provided by Cloud Run
ENV PORT=8080

# Run uvicorn as a module using the backend package
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
