FROM postgres:16-alpine

ENV POSTGRES_USER=genvideo \
    POSTGRES_PASSWORD=genvideo \
    POSTGRES_DB=genvideo

EXPOSE 5432

COPY ./docs /docker-entrypoint-initdb.d/
