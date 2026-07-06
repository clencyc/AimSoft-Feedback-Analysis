# this is a multi-stage Dockerfile for building and 
# running a Python application using Gunicorn as the WSGI server.

FROM python:3.13-slim AS builder

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

# Install build dependencies needed for packages like psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# stage 2: Production stage

FROM python:3.13-slim
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "backend.wsgi:application"]
