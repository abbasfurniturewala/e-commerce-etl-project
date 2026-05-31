from __future__ import annotations

import os
import subprocess
from datetime import date, datetime, timezone

from airflow.sdk import dag, task


@dag(
    dag_id="olist_daily_ingestion",
    description="Replay and ingest one historical Olist business day.",
    schedule=None,
    start_date=datetime(2016, 9, 4, tzinfo=timezone.utc),
    catchup=False,
    params={"batch_date": "2016-09-13"},
    tags=["ecommerce", "ingestion", "olist"],
)
def olist_daily_ingestion():
    @task
    def initialize_raw_schema() -> None:
        from ecommerce_pipeline.config import Settings
        from ecommerce_pipeline.db import initialize_schema

        settings = Settings()
        initialize_schema(settings.postgres_dsn, settings.schema_path)

    @task
    def replay_batch(batch_date: str) -> dict[str, int]:
        from ecommerce_pipeline.config import Settings
        from ecommerce_pipeline.replay import generate_daily_batch

        settings = Settings()
        return generate_daily_batch(
            settings.source_dir,
            settings.landing_dir,
            date.fromisoformat(batch_date),
        )

    @task
    def ingest_batch(batch_date: str) -> dict[str, int]:
        from ecommerce_pipeline.config import Settings
        from ecommerce_pipeline.db import load_batch

        settings = Settings()
        return load_batch(
            settings.postgres_dsn,
            settings.landing_dir,
            date.fromisoformat(batch_date),
        )

    @task
    def build_warehouse() -> None:
        project_dir = os.environ["DBT_PROJECT_DIR"]
        profiles_dir = os.environ["DBT_PROFILES_DIR"]
        subprocess.run(
            [
                "dbt",
                "build",
                "--project-dir",
                project_dir,
                "--profiles-dir",
                profiles_dir,
            ],
            check=True,
        )

    batch_date = "{{ params.batch_date }}"
    schema_ready = initialize_raw_schema()
    landing_rows = replay_batch(batch_date)
    loaded_rows = ingest_batch(batch_date)
    warehouse_built = build_warehouse()

    schema_ready >> landing_rows >> loaded_rows >> warehouse_built


olist_daily_ingestion()
