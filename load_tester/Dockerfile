# Use lightweight Python image
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy test script
COPY test_crypto.py .

# Run script
CMD ["python", "test_crypto.py"]