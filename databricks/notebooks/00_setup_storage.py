# Databricks notebook source
import json


def widget(name: str, default: str) -> str:
    dbutils.widgets.text(name, default)
    return dbutils.widgets.get(name)


def quoted(identifier: str) -> str:
    return f"`{identifier.replace('`', '``')}`"


catalog = widget("catalog", "") or spark.sql("select current_catalog()").first()[0]
bronze_schema = widget("bronze_schema", "ecommerce_bronze")
silver_schema = widget("silver_schema", "ecommerce_silver")
gold_schema = widget("gold_schema", "ecommerce_gold")
landing_volume = widget("landing_volume", "landing")

for schema in (bronze_schema, silver_schema, gold_schema):
    spark.sql(f"create schema if not exists {quoted(catalog)}.{quoted(schema)}")

spark.sql(
    f"""
    create volume if not exists
        {quoted(catalog)}.{quoted(bronze_schema)}.{quoted(landing_volume)}
    """
)

landing_path = f"/Volumes/{catalog}/{bronze_schema}/{landing_volume}"
print(
    json.dumps(
        {
            "catalog": catalog,
            "bronze_schema": bronze_schema,
            "silver_schema": silver_schema,
            "gold_schema": gold_schema,
            "landing_volume": landing_volume,
            "landing_path": landing_path,
        },
        indent=2,
    )
)
