FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && pip install --upgrade pip && apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN mkdir -p /app/uploads && groupadd -r test_user && useradd -r -g test_user -u 1000 test_user

RUN chown -R test_user:test_user /app

USER test_user

CMD ["fastapi", "dev", "app/main.py"]
