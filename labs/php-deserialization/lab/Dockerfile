FROM php:8.2-cli-alpine
RUN apk add --no-cache openssl
COPY index.php /app/index.php
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
