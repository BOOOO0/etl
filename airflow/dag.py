from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# DAG 정의
with DAG(
    dag_id="historical_stock_etl",
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="Fetch historical stock data for 1 year",
    schedule_interval="10 1 * * *",  # 월~금, 한국 시간 오후 5시 (UTC 8시)
    start_date=datetime(2023, 12, 23),  # 1년 전 데이터 시작
    catchup=True,  # 과거 실행 허용
) as dag:

    # ETL 작업 실행
    run_etl_task = BashOperator(
        task_id="run_etl_job",
        bash_command=(
            "spark-submit "
            "--master yarn "
            "--deploy-mode cluster "
            "/home/hadoop/api_etl.py "
            "--date {{ ds }}"  # 실행 날짜 전달 (YYYY-MM-DD 형식)
        ),
    )
