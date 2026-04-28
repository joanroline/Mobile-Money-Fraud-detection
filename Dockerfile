# Use official Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir flask flask-cors pandas joblib scikit-learn openpyxl gunicorn

# Expose port 7860 — this is the port Hugging Face always uses
EXPOSE 7860

# Start the Flask API using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "api.risk_status_api:app"]

# Create models directory
RUN mkdir -p /app/models

# Download model
RUN apt-get update && apt-get install -y wget
RUN wget -O /app/models/random_forest.pkl \
    https://huggingface.co/JoanRoline22/wave-fraud-model/resolve/main/random_forest.pkl

    CMD ["python", "main.py"]