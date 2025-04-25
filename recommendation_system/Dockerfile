FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ca-certificates curl && \
    update-ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/model_cache && chmod 777 /app/model_cache

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/model

COPY model/products_data.json /app/model/

COPY app/ /app/app/

ENV MODEL_PATH="sentence-transformers/all-MiniLM-L6-v2"
ENV PRODUCTS_DATA_PATH="/app/model/products_data.json"
ENV PYTHONWARNINGS="ignore::Warning"
ENV PYTHONIOENCODING="utf-8"
ENV SSL_CERT_DIR="/etc/ssl/certs"
ENV REQUESTS_CA_BUNDLE=""
ENV CURL_CA_BUNDLE=""
ENV HF_HUB_DISABLE_SYMLINKS_WARNING="1"
ENV PYTHONHTTPSVERIFY="0"

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]