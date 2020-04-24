COMPONENT=$1
INITIALIZE_DB=$2

if [ "${INITIALIZE_DB}" = "initialize" ];
then
  airflow initdb
fi

if [ "${COMPONENT}" = "flower" ];
then
  echo "starting worker shutdown service"
  nohup python ${AIRFLOW_HOME}/airflow_worker_shutdown_service.py > /tmp/airflow_worker_shutdown_service.log 2>&1 &
  echo "starting metric logging process"
  nohup python ${AIRFLOW_HOME}/metrics_logger.py > /tmp/metrics_logger.log 2>&1 &
fi

echo "starting airflow component "$COMPONENT

airflow ${COMPONENT}

echo ${COMPONENT} " stopped."
echo "waiting for pod termination by controller."

# Don't want to terminate the entrypoint script, else the controller will
# restart the container.
sleep infinity
