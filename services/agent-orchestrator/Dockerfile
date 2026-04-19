FROM python:3.11-slim AS builder

RUN pip install hatchling

WORKDIR /app
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install -e . --no-cache-dir

# ── Runtime image ────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ ./src/

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

CMD ["python", "-m", "orhashield"]
