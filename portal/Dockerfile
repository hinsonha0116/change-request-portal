# Change Request Portal. Build from this folder:  docker build -t change-request-portal:0.1.0 .
# BASE_IMAGE lets a cluster with no internet access point at its own mirror of the Python image.
ARG BASE_IMAGE=python:3.13-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY manage.py .
COPY config config
COPY accounts accounts
COPY changes changes

# Static files are collected at build time, so the running container never writes to disk.
RUN DJANGO_SECRET_KEY=build-only DJANGO_ALLOWED_HOSTS=build python manage.py collectstatic --noinput \
 && python -m compileall -q .

# Runs as an unprivileged user with a numeric ID, so runAsNonRoot can be enforced.
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin portal
USER 10001

EXPOSE 8000

# Worker heartbeat files go to memory (/dev/shm), so the root file system can be read-only.
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "60", \
     "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", \
     "--forwarded-allow-ips", "*"]
