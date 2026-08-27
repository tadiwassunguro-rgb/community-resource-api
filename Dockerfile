FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
ENV DATABASE_PATH=/app/data/resources.db

RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "run.py"]
