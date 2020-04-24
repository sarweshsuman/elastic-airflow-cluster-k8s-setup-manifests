FROM python:3.6.10-slim-stretch

RUN apt-get update \
    && apt-get -y install build-essential \
    && pip install apache-airflow[postgres,celery,rabbitmq] \
    && apt-get -y install procps

ENV AIRFLOW_HOME /home/airflow
ENV PATH ${AIRFLOW_HOME}/dags:${AIRFLOW_HOME}/plugins:$PATH
ENV PYTHONPATH ${AIRFLOW_HOME}/dags:${AIRFLOW_HOME}/plugins:$PYTHONPATH

RUN useradd -c "Airflow User" -u 1020 airflow \
    && mkdir -p ${AIRFLOW_HOME}/dags \
    && mkdir -p ${AIRFLOW_HOME}/plugins \
    && mkdir -p ${AIRFLOW_HOME}/logs \
    && mkdir -p ${AIRFLOW_HOME}/logs/scheduler \
    && chmod -R 777 ${AIRFLOW_HOME} \
    && chmod -R 777 /var \
    && chmod -R 777 /tmp \
    && chmod -R 777 /etc

RUN pip install redis

COPY airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
COPY entrypoint.sh /entrypoint.sh
COPY airflow_worker_shutdown_service.py ${AIRFLOW_HOME}/airflow_worker_shutdown_service.py
COPY metrics_logger.py ${AIRFLOW_HOME}/metrics_logger.py

RUN chmod +x /entrypoint.sh
RUN chmod +x ${AIRFLOW_HOME}/airflow_worker_shutdown_service.py
RUN chmod +x ${AIRFLOW_HOME}/metrics_logger.py

EXPOSE 8080 5555 5559 8793

USER airflow
WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["/bin/bash","/entrypoint.sh"]
