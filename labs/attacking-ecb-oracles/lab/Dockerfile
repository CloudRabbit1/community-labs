# python:3.11-slim-bookworm — no extra crypto libs needed; uses openssl binary
FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends openssl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY app.py .
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh
EXPOSE 5000
CMD ["/bin/sh", "-c", "/setup.sh && python3 app.py"]
