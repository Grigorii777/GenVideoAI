FROM rabbitmq:3.13-management

ENV RABBITMQ_DEFAULT_USER=guest \
    RABBITMQ_DEFAULT_PASS=guest \
    RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS="-rabbitmq_stream advertised_host localhost"

EXPOSE 5672 15672

CMD ["rabbitmq-server"]
