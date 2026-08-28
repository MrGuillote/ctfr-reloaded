FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY ctfr_reloaded ./ctfr_reloaded
COPY ctfr.py ./

RUN pip install --no-cache-dir .

ENTRYPOINT ["ctfr-reloaded"]
