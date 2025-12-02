from airflow.decorators import dag, task
from datetime import datetime

@dag(
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['basic_taskflow']
)


def taskflow():

    @task
    def task_a():
        print("Task A is running")
        return 21
    
    @task
    def task_b(value):
        print(f"Task B received value: {value}")

    task_b(task_a())




basic_taskflow_dag = taskflow()