#!/bin/sh
# Run both API and Celery worker in the same container
celery -A app.worker.celery_app worker --loglevel=info --concurrency=2 &
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
