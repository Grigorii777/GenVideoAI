FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /docs

COPY . .

RUN pip install --upgrade pip \
    && pip install mkdocs mkdocs-material

EXPOSE 8000

CMD ["python", "-m", "http.server", "8000"]
