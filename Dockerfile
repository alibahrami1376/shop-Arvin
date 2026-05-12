FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .

RUN pip config set global.index-url https://mirror-pypi.runflare.com/simple && \
    pip install --no-cache-dir -r requirements.txt

COPY ./core /app

RUN python manage.py collectstatic --noinput --clear || true

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
