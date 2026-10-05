FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY app/common /app/app/common
COPY app/payment-service /app/app/payment-service
COPY app/payment-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
USER 10001
EXPOSE 8004
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8004/health')"
CMD ["uvicorn","app.payment-service.main:app","--host","0.0.0.0","--port","8004"]
