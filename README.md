# E-Commerce Data Engineering Project

This project replays the public Olist e-commerce dataset as daily batches and builds an
analytics pipeline incrementally. The current milestone lands source files, loads an
idempotent PostgreSQL raw layer, and orchestrates a tested dbt analytics warehouse with
Airflow. A serverless Databricks lakehouse builds Bronze, Silver, and Gold Delta tables;
Databricks SQL and Power BI analytics remain the next milestone.

## Architecture

```text
Olist CSV files
    -> Python daily replay generator
    -> PostgreSQL raw schema
    -> Airflow orchestration
    -> dbt staging and marts
    -> Databricks Bronze/Silver/Gold Delta tables
    -> Databricks SQL / Power BI
```

## Phase 1 Setup

1. Create a local Python environment and install the package:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e .
   ```

2. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Download the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
   and place its nine CSV files in `data/source/`. Keep downloaded data out of Git.

4. Inspect the source:

   ```powershell
   ecommerce-pipeline inspect-source
   ```

5. Start PostgreSQL and initialize the raw schema:

   ```powershell
   docker compose up -d postgres
   ecommerce-pipeline init-db
   ```

6. Replay and ingest one day from the source date range reported by the inspect command:

   ```powershell
   ecommerce-pipeline run-batch --date 2017-01-05
   ```

Daily landing files are written beneath `data/landing/YYYY-MM-DD/`. The raw schema stores
all source values as text, adds ingestion metadata, hashes each row for idempotency, and
records loaded file checksums in `raw.ingested_files`. The file audit stores both the
source row count and the number of rows inserted after deduplication.

## Airflow

The local Airflow service uses `airflow standalone` for development and learning. Start
it after PostgreSQL is healthy:

```powershell
docker compose up -d airflow
docker compose logs airflow
```

Open `http://localhost:8080` and use the admin credentials printed in the logs. Trigger
the `olist_daily_ingestion` DAG manually. Its `batch_date` parameter defaults to
`2016-09-13`; change that ISO date to replay another historical source day.

The DAG runs four tasks in order: initialize the raw schema, generate a daily landing
batch, ingest the raw records, and run `dbt build` so every warehouse refresh is tested.

Standalone Airflow keeps the local setup small. A deployment-oriented version should
split its components and use a dedicated metadata database.

## dbt Warehouse

Install the warehouse dependencies and validate the local Postgres connection:

```powershell
pip install -e ".[warehouse]"
dbt debug --project-dir dbt --profiles-dir dbt
```

Build the typed staging views, star-schema tables, daily-sales mart, and data tests:

```powershell
dbt build --project-dir dbt --profiles-dir dbt
```

dbt creates:

| Schema | Purpose |
| --- | --- |
| `analytics_staging` | Typed, cleaned source-aligned views |
| `analytics_warehouse` | Date, customer, product, seller, and geography dimensions plus order facts |
| `analytics_marts` | Daily sales, delivery performance, seller performance, and customer RFM summaries |

The original Olist reviews file contains repeated `review_id` values. Staging retains
the latest answered record for each review identifier before order-level aggregation.

## Useful Commands

```powershell
ecommerce-pipeline replay --date 2017-01-05
ecommerce-pipeline ingest --date 2017-01-05
dbt build --project-dir dbt --profiles-dir dbt
python -m unittest discover -s tests -v
docker compose up -d airflow
docker compose down
```

## Databricks Lakehouse

The repository includes a serverless Databricks Declarative Automation Bundle with
Bronze, Silver, and Gold PySpark notebooks. See
[`databricks/README.md`](databricks/README.md) for authentication, deployment, landing
file upload, and job execution steps.

## Roadmap

- Add validation tasks and a replay cursor to the Airflow ingestion DAG.
- Add Databricks SQL queries and a starter analytics dashboard over the Gold marts.
- Connect Power BI to the final reporting marts.
