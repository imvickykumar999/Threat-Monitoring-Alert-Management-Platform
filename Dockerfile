FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos '' django \
    && mkdir -p /app/staticfiles \
    && chown -R django:django /app

USER django

CMD ["gunicorn", "threat_monitoring_platform.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
