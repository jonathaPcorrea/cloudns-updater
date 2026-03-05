FROM python:3.12-alpine

WORKDIR /app

COPY dynamic_ip.py .

CMD ["python", "-u", "dynamic_ip.py"]
