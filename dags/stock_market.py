from airflow.decorators import dag, task
from airflow.sensors.base import PokeReturnValue
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from datetime import datetime

from include.stock_market.tasks import _get_stock_prices

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

    is_api_available() >> get_stock_prices


stock_market_dag = stock_market()

