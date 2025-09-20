FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.8.3

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install "poetry==${POETRY_VERSION}" \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction

CMD ["python"]
