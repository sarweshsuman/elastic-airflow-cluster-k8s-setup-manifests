FROM rabbitmq:management

# Define environment variables.
ENV RABBITMQ_USER airflow
ENV RABBITMQ_PASSWORD airflow
ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5672 15672

CMD ["/entrypoint.sh"]
