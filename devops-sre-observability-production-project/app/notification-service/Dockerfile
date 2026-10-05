FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY app/common /app/app/common
COPY app/notification-service /app/app/notification-service
COPY app/notification-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
USER 10001
EXPOSE 8005
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8005/health')"
CMD ["uvicorn","app.notification-service.main:app","--host","0.0.0.0","--port","8005"]
