# Aragorn: the only Rivendell container that mounts the Docker socket.
# Build context is the repository root (see docker-compose.yml).
FROM python:3.12-alpine

WORKDIR /app
COPY src/common/aragorn /app/aragorn
COPY src/web/aragorn/server.py /app/aragorn_server.py

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 5690
# Runs as root: the socket inside the Docker Desktop / OrbStack VM is root-owned.
CMD ["python3", "/app/aragorn_server.py"]
