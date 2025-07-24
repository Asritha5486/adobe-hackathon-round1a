FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Only copy what’s needed
COPY process_pdfs.py .
COPY heading_model.joblib .
COPY label_encoder.joblib .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "process_pdfs.py"]