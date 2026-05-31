# SQL Analytics Layer

These queries are designed for Databricks SQL, AI/BI dashboards, and Power BI reporting
over the `workspace.ecommerce_gold` schema.

| Query | Suggested dashboard tile |
| --- | --- |
| `01_executive_kpis.sql` | KPI counters |
| `02_daily_sales.sql` | Revenue and order trend line |
| `03_delivery_performance.sql` | Late-delivery and delivery-time trend |
| `04_top_sellers.sql` | Top-seller bar chart or table |
| `05_customer_rfm_segments.sql` | Customer-segment bar or pie chart |
| `06_sales_by_customer_state.sql` | Revenue-by-state bar chart or map |

Validate every query against the configured SQL warehouse from the repository root:

```powershell
$env:DATABRICKS_SQL_WAREHOUSE_ID = "9246515affbaccaf"
powershell -ExecutionPolicy Bypass -File .\databricks\scripts\validate_sql_queries.ps1
```

## Power BI Desktop

Use the Databricks connector with OAuth and these SQL warehouse settings:

| Setting | Value |
| --- | --- |
| Server hostname | `dbc-ac08fa05-89b5.cloud.databricks.com` |
| HTTP path | `/sql/1.0/warehouses/9246515affbaccaf` |
| Catalog | `workspace` |
| Schema | `ecommerce_gold` |

Start with Import mode for this portfolio-sized dataset. DirectQuery remains available
if the project grows enough to require live queries from Power BI.

## AI/BI Dashboard

The bundle deploys a starter dashboard named `Ecommerce Analytics` from
`../dashboards/ecommerce_analytics.lvdash.json`. Open it from the Databricks Dashboards
sidebar after running `databricks bundle deploy -t dev`.
