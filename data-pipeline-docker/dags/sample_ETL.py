from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys

from script1 import load_inventory_from_mongo
from script2 import load_order_and_delivery_data
from script3 import process_final_logic
from script4 import update_ordercycle_logic

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    dag_id='sample_ETL',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=['ecommerce'],
) as dag:

    task1 = PythonOperator(
        task_id='load_inventory_from_mongo',
        python_callable=load_inventory_from_mongo,
    )

    task2 = PythonOperator(
        task_id='load_order_and_delivery_data',
        python_callable=load_order_and_delivery_data,
    )

    task3 = PythonOperator(
        task_id='process_final_logic',
        python_callable=process_final_logic,
    )
    
    task4 = PythonOperator(
        task_id='update_ordercycle_logic',
        python_callable=update_ordercycle_logic,
    )


    task1 >> task2 >> task3 >> task4
