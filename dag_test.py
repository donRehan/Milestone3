from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from task_1 import ms_1
#from task_2 import task_2

default_args = {
    'owner': 'Data Engineer',
    'start_date': datetime(2023, 1, 1),
}

dag = DAG(
#Make this workflow happens only once
    dag_id='crm-elastic-dag',
    default_args=args,
    schedule_interval='@once'

)

with dag:
    task_1 = PythonOperator(
        task_id='task_1',
        python_callable=ms_1,
    )

    """
    task_2 = PythonOperator(
        task_id='task_2',
        python_callable=ms_2,
    )
    """
    task_1 >> task_2

#
#task_1 = PythonOperator(
#
#)
#
#task_2 = PythonOperator(
#
#)
