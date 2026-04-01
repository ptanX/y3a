FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src/ ./services/notification_service/

EXPOSE 8002

CMD ["uvicorn", "services.notification_service.main:app", "--host", "0.0.0.0", "--port", "8002"]
