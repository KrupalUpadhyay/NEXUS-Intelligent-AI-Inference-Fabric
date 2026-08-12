FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
# XGBoost is a large wheel; use resilient download settings for slower networks.
RUN pip install --no-cache-dir --retries 5 --timeout 300 -r requirements.txt

COPY backend/app ./app
COPY backend/models ./models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
