FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install .

EXPOSE 4317 9464

CMD ["python"]
