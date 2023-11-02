web: gunicorn -w 2 -k uvicorn.workers.UvicornWorker biblebee_api:app
worker: celery -A biblebee_api.worker.celery worker --loglevel=info
scheduler: celery -A biblebee_api.scheduler beat
