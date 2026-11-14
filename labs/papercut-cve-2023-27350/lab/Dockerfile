FROM python:3.12-slim
WORKDIR /app
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh && /setup.sh
COPY app.py /app/app.py
EXPOSE 8080
CMD ["python3", "/app/app.py"]
