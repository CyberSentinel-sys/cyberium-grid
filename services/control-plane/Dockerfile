FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "orhashield_cp.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
