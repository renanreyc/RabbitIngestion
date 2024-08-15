# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /mnt/ncs-ingestion-temp-file

COPY src/ /app/src/

EXPOSE 8079

# Run the application.
CMD ["python", "src/process.py"]
