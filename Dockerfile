FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 SHAHID_MODE=hosted
WORKDIR /app
COPY requirements-lock.txt ./
RUN pip install --no-cache-dir -r requirements-lock.txt \
    && groupadd --gid 10001 shahid \
    && useradd --uid 10001 --gid 10001 --no-create-home shahid \
    && mkdir -p /app/state && chown 10001:10001 /app/state
COPY app ./app
COPY shahid ./shahid
COPY samples ./samples
COPY scripts ./scripts
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-proxy-headers", "--no-access-log", "--limit-concurrency", "32", "--timeout-keep-alive", "5"]
