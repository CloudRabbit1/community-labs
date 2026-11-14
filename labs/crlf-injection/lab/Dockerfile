FROM python:3.12-slim
RUN apk add --no-cache openssl 2>/dev/null || apt-get install -y --no-install-recommends openssl 2>/dev/null || true
COPY app.py /app/app.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
