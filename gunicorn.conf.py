import os

workers = int(os.environ.get('GUNICORN_WORKERS', 2))
threads = int(os.environ.get('GUNICORN_THREADS', 4))
worker_timeout = int(os.environ.get('GUNICORN_TIMEOUT', 30))
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"