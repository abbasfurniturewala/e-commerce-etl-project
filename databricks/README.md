# Databricks Lakehouse Layer

This directory contains a Databricks Declarative Automation Bundle for the Olist
e-commerce lakehouse layer. The notebooks use serverless Lakeflow Jobs and Unity Catalog
managed storage, which fits Databricks Free Edition.

## Workflow

```text
Local immutable landing batches
    -> Unity Catalog managed landing volume
    -> Bronze Delta tables
    -> Silver typed and deduplicated Delta tables
    -> Gold facts, dimensions, and analytics marts
```

## First Deployment

1. Install the Databricks CLI and authenticate against the workspace:

   ```powershell
   winget install Databricks.DatabricksCLI
   databricks auth login --host https://dbc-ac08fa05-89b5.cloud.databricks.com
   ```

2. Validate and deploy the bundle from the repository root:

   ```powershell
   databricks bundle validate -t dev
   databricks bundle deploy -t dev
   ```

3. Create the Unity Catalog schemas and managed landing volume:

   ```powershell
   databricks bundle run -t dev ecommerce_setup_job
   ```

   The development bundle uses the writable `workspace` catalog and prints the managed
   volume path.

4. Upload locally replayed landing batches:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\databricks\scripts\upload_landing.ps1 -Catalog workspace
   ```

5. Run the Bronze, Silver, and Gold jobs:

   ```powershell
   databricks bundle run -t dev ecommerce_lakehouse_pipeline
   ```

The setup and ingestion operations are idempotent. Bronze rows merge by source-row hash,
while Silver and Gold tables are rebuilt from the current Bronze state.
