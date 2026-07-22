"""Daily orchestration for the synthetic claims platform."""

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="insurance_claims_daily",
    description="Generate, validate and transform synthetic insurance claims",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["insurance", "data-engineering", "portfolio"],
) as dag:
    generate = BashOperator(
        task_id="generate_claim_events",
        bash_command=(
            "python -m claims_platform.generator --count 1000 --seed {{ ds_nodash }} "
            "--output /opt/airflow/data/raw/claims_{{ ds_nodash }}.jsonl"
        ),
    )

    validate = BashOperator(
        task_id="validate_claim_events",
        bash_command=(
            "python -m claims_platform.pipeline "
            "--input /opt/airflow/data/raw/claims_{{ ds_nodash }}.jsonl "
            "--output /opt/airflow/data/validated/claims_{{ ds_nodash }}.jsonl "
            "--quality-report /opt/airflow/data/quality/report_{{ ds_nodash }}.json"
        ),
    )

    transform = BashOperator(
        task_id="spark_transform",
        bash_command=(
            "spark-submit /opt/airflow/spark/transform_claims.py "
            "--input /opt/airflow/data/validated/claims_{{ ds_nodash }}.jsonl "
            "--output /opt/airflow/data/curated/claims "
            "--quarantine /opt/airflow/data/quarantine/claims_{{ ds_nodash }}"
        ),
    )

    generate >> validate >> transform
