# ---Etap 1: budildin enviorement ---
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# --- Etap 2: Final app ---
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

ENV PYTHONUNBUFFERED=1

# Komendy - uruchom aplikację (zmienić później pod gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

