FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    rabbitmq-server \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get install rabbitmq-server>=3.8 -y --fix-missing

RUN rabbitmq-plugins enable rabbitmq_management

ENV RABBITMQ_PID_FILE=/var/lib/rabbitmq/mnesia/rabbitmq

COPY . .
RUN chmod +x /init.sh
EXPOSE 15672

CMD ["/init.sh"]
