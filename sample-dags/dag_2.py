from builtins import range
from datetime import timedelta

import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(0),
}

dag = DAG(
    dag_id='dag_2',
    default_args=args,
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=5),
)

task_1 = BashOperator(
    task_id='task_1',
    bash_command='sleep 100',
    dag=dag,
)

task_2 = BashOperator(
    task_id='task_2',
    bash_command='echo sarwesh',
    dag=dag,
)

task_1 >> task_2
