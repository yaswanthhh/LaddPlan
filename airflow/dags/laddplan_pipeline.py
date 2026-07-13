from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "laddplan",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="laddplan_pipeline",
    description="Load LaddPlan data, build dbt models, and run charger optimisation.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["laddplan", "ev", "dbt", "networkx"],
) as dag:

    load_csv_data = BashOperator(
        task_id="load_csv_data",
        bash_command=(
            "cd /opt/airflow/laddplan && "
            "python src/ingestion/load_csv_to_postgres.py"
        ),
    )

    build_dbt_models = BashOperator(
        task_id="build_dbt_models",
        bash_command=(
            "cd /opt/airflow/laddplan && "
            "dbt build "
            "--project-dir dbt/laddplan "
            "--profiles-dir dbt/laddplan"
        ),
    )

    run_coverage_optimizer = BashOperator(
        task_id="run_coverage_optimizer",
        bash_command=(
            "cd /opt/airflow/laddplan && "
            "python charger_coverage.py"
        ),
    )

    load_csv_data >> build_dbt_models >> run_coverage_optimizer