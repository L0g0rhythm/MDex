# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user for Zero Trust (Module 02)
RUN groupadd -r mdex && useradd -r -g mdex mdex \
    && mkdir -p /app/Downloads /app/logs \
    && chown -r mdex:mdex /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .
RUN chown -R mdex:mdex /app

USER mdex

# Module 23: Resource Stewardship - Limit memory/cpu via compose
EXPOSE 8000

CMD ["python", "src/main.py"]
