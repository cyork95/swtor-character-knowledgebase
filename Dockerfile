FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data volume mount point
RUN mkdir -p /data

ENV SWTOR_DB_PATH=/data/swtor.db
ENV FLASK_ENV=production

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "app:create_app()"]
