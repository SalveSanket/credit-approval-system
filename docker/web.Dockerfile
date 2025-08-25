FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /app
ENV PYTHONUNBUFFERED=1
CMD ["bash","-lc","python manage.py makemigrations && python manage.py migrate && gunicorn credit_core.wsgi:application -b 0.0.0.0:8000"]
