FROM python:3.12-slim
WORKDIR /app
COPY setup.sh /app/setup.sh
COPY app.py /app/app.py
RUN chmod +x /app/setup.sh
EXPOSE 8080
CMD ["/bin/sh", "-c", "/app/setup.sh && python3 /app/app.py"]
