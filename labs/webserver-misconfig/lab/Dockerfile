FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 python3 openssl iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod cgi cgid

COPY apache2.conf /etc/apache2/sites-enabled/000-default.conf
COPY status.sh /usr/lib/cgi-bin/status.sh
RUN chmod 755 /usr/lib/cgi-bin/status.sh

RUN echo '<html><body><h1>Corporate Intranet</h1><p>Internal tools: <a href="/cgi-bin/status.sh?host=127.0.0.1">Network Status</a></p></body></html>' \
    > /var/www/html/index.html

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
