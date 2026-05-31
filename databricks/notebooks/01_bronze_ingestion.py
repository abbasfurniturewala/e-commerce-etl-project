# Databricks notebook source
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType


def widget(name: str, default: str) -> str:
    dbutils.widgets.text(name, default)
    return dbutils.widgets.get(name)


def quoted(identifier: str) -> str:
    return f"`{identifier.replace('`', '``')}`"


catalog = widget("catalog", "") or spark.sql("select current_catalog()").first()[0]
bronze_schema = widget("bronze_schema", "ecommerce_bronze")
landing_volume = widget("landing_volume", "landing")
landing_path = f"/Volumes/{catalog}/{bronze_schema}/{landing_volume}"

datasets = {
    "olist_orders": (
        "olist_orders_dataset.csv",
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    ),
    "olist_order_items": (
        "olist_order_items_dataset.csv",
        [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ],
    ),
    "olist_order_payments": (
        "olist_order_payments_dataset.csv",
        [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ],
    ),
    "olist_order_reviews": (
        "olist_order_reviews_dataset.csv",
        [
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ],
    ),
    "olist_customers": (
        "olist_customers_dataset.csv",
        [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ],
    ),
    "olist_products": (
        "olist_products_dataset.csv",
        [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ],
    ),
    "olist_sellers": (
        "olist_sellers_dataset.csv",
        [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ],
    ),
    "olist_geolocation": (
        "olist_geolocation_dataset.csv",
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ],
    ),
    "product_category_name_translation": (
        "product_category_name_translation.csv",
        [
            "product_category_name",
            "product_category_name_english",
        ],
    ),
}

spark.sql(f"create schema if not exists {quoted(catalog)}.{quoted(bronze_schema)}")

for table_name, (filename, columns) in datasets.items():
    csv_schema = StructType([StructField(column, StringType(), True) for column in columns])
    source_path = f"{landing_path}/*/{filename}"
    source_rows = (
        spark.read.option("header", True)
        .schema(csv_schema)
        .csv(source_path)
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn(
            "_batch_date",
            F.regexp_extract(F.col("_source_file"), r"/(\d{4}-\d{2}-\d{2})/", 1).cast("date"),
        )
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_row_hash", F.sha2(F.to_json(F.struct(*[F.col(column) for column in columns])), 256))
        .dropDuplicates(["_row_hash"])
    )

    full_table_name = f"{quoted(catalog)}.{quoted(bronze_schema)}.{quoted(table_name)}"
    if spark.catalog.tableExists(f"{catalog}.{bronze_schema}.{table_name}"):
        (
            DeltaTable.forName(spark, f"{catalog}.{bronze_schema}.{table_name}")
            .alias("target")
            .merge(source_rows.alias("source"), "target._row_hash = source._row_hash")
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        source_rows.write.format("delta").mode("overwrite").saveAsTable(full_table_name)

    print(f"{full_table_name}: {spark.table(full_table_name).count()} Bronze rows")
