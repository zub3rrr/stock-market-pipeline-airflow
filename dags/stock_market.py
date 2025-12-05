from airflow.decorators import dag, task
from airflow.sensors.base import PokeReturnValue
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from astro import sql as aql
from astro.files import File
from astro.sql.table import Table, Metadata
from datetime import datetime

from include.stock_market.tasks import _get_stock_prices , _store_prices , _get_formatted_csv , BUCKET_NAME

SYMBOL = "NVDA"

@dag(
    start_date=datetime(2023, 1, 1),
    schedule='@daily',
    catchup=False,    
    tags=['stock_market']
)
# 1. catchup false means , no previous runs will be backfilled from Jan 1, 2023 to today if the DAG is started today. Only future scheduled runs will be executed.
# 2. tags are used to categorize and filter DAGs in the Airflow UI.
def stock_market():
    
    @task.sensor(poke_interval=30, timeout=300, mode='poke')
    def is_api_available()-> PokeReturnValue:
        import requests
        try:
            api = BaseHook.get_connection("stock_api")
            url = f"{api.host}{api.extra_dejson['endpoint']}"
            print(url)
            response = requests.get(url,headers=api.extra_dejson['headers'])
            condition = response.json()['finance']['result'] is None
            return PokeReturnValue(is_done=condition, xcom_value=url)
        except Exception as e:
            return PokeReturnValue(is_done=False, xcom_value=str(e))
        

    get_stock_prices = PythonOperator(
        task_id = 'get_stock_prices',
        python_callable = _get_stock_prices,
        # op_kwargs = {'url': 'https://query1.finance.yahoo.com/v8/finance/chart/','symbol': SYMBOL}
        op_kwargs = {'url': '{{ti.xcom_pull(task_ids="is_api_available")}}','symbol': SYMBOL}
    )

    #templating "{{ti.xcom_pull(task_ids="is_api_available")}}" is used to dynamically fetch the URL from the XCom pushed by the is_api_available sensor task.

    store_prices = PythonOperator(
        task_id='store_prices',
        python_callable=_store_prices,
        op_kwargs={'stock': '{{ ti.xcom_pull(task_ids="get_stock_prices") }}'}
    )

    format_prices = DockerOperator(
        task_id='format_prices',
        image='airflow/stock-app',
        container_name='format_prices',
        api_version='auto',
        auto_remove='success',
        docker_url='tcp://docker-proxy:2375',
        network_mode='container:spark-master',
        tty=True,
        xcom_all=False,
        mount_tmp_dir=False,
        environment={
            'SPARK_APPLICATION_ARGS': '{{ ti.xcom_pull(task_ids="store_prices") }}'
        }
    )

    get_formatted_csv = PythonOperator(
        task_id='get_formatted_csv',
        python_callable=_get_formatted_csv,
        op_kwargs={
            'path': '{{ ti.xcom_pull(task_ids="store_prices") }}'
        }
    )

    load_to_dw = aql.load_file(
        task_id='load_to_dw',
        input_file=File(
            path=f"s3://{BUCKET_NAME}/{{{{ ti.xcom_pull(task_ids='get_formatted_csv') }}}}",
            conn_id='minio'
        ),
        output_table=Table(
            name='stock_market',
            conn_id='postgres',
            metadata=Metadata(
                schema='public'
            )
        ),
        load_options={
            "aws_access_key_id": BaseHook.get_connection('minio').login,
            "aws_secret_access_key": BaseHook.get_connection('minio').password,
            "endpoint_url": BaseHook.get_connection('minio').host,
        }
    )

    is_api_available() >> get_stock_prices >> store_prices >> format_prices >> get_formatted_csv >> load_to_dw


stock_market_dag = stock_market()

