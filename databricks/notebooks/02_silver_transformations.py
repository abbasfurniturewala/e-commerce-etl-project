# Databricks notebook source
from pyspark.sql import Window
from pyspark.sql import functions as F


def widget(name: str, default: str) -> str:
    dbutils.widgets.text(name, default)
    return dbutils.widgets.get(name)


def quoted(identifier: str) -> str:
    return f"`{identifier.replace('`', '``')}`"


catalog = widget("catalog", "") or spark.sql("select current_catalog()").first()[0]
bronze_schema = widget("bronze_schema", "ecommerce_bronze")
silver_schema = widget("silver_schema", "ecommerce_silver")


def bronze(table_name: str):
    return spark.table(f"{catalog}.{bronze_schema}.{table_name}")


def write_silver(table_name: str, dataframe) -> None:
    full_table_name = f"{quoted(catalog)}.{quoted(silver_schema)}.{quoted(table_name)}"
    (
        dataframe.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(full_table_name)
    )
    print(f"{full_table_name}: {dataframe.count()} Silver rows")


spark.sql(f"create schema if not exists {quoted(catalog)}.{quoted(silver_schema)}")

orders = bronze("olist_orders").selectExpr(
    "_row_hash as source_row_hash",
    "_batch_date as batch_date",
    "_ingested_at as ingested_at",
    "nullif(order_id, '') as order_id",
    "nullif(customer_id, '') as customer_id",
    "nullif(order_status, '') as order_status",
    "try_cast(nullif(order_purchase_timestamp, '') as timestamp) as order_purchase_at",
    "try_cast(nullif(order_approved_at, '') as timestamp) as order_approved_at",
    "try_cast(nullif(order_delivered_carrier_date, '') as timestamp) as order_delivered_carrier_at",
    "try_cast(nullif(order_delivered_customer_date, '') as timestamp) as order_delivered_customer_at",
    "try_cast(nullif(order_estimated_delivery_date, '') as timestamp) as order_estimated_delivery_at",
)
write_silver("orders", orders)

order_items = bronze("olist_order_items").selectExpr(
    "sha2(concat_ws('||', order_id, order_item_id), 256) as order_item_sk",
    "_row_hash as source_row_hash",
    "_batch_date as batch_date",
    "_ingested_at as ingested_at",
    "nullif(order_id, '') as order_id",
    "try_cast(nullif(order_item_id, '') as int) as order_item_id",
    "nullif(product_id, '') as product_id",
    "nullif(seller_id, '') as seller_id",
    "try_cast(nullif(shipping_limit_date, '') as timestamp) as shipping_limit_at",
    "try_cast(nullif(price, '') as decimal(12, 2)) as item_price",
    "try_cast(nullif(freight_value, '') as decimal(12, 2)) as freight_value",
)
write_silver("order_items", order_items)

order_payments = bronze("olist_order_payments").selectExpr(
    "sha2(concat_ws('||', order_id, payment_sequential), 256) as payment_sk",
    "_row_hash as source_row_hash",
    "_batch_date as batch_date",
    "_ingested_at as ingested_at",
    "nullif(order_id, '') as order_id",
    "try_cast(nullif(payment_sequential, '') as int) as payment_sequence",
    "nullif(payment_type, '') as payment_type",
    "try_cast(nullif(payment_installments, '') as int) as payment_installments",
    "try_cast(nullif(payment_value, '') as decimal(12, 2)) as payment_value",
)
write_silver("order_payments", order_payments)

review_versions = bronze("olist_order_reviews").selectExpr(
    "_row_hash as source_row_hash",
    "_batch_date as batch_date",
    "_ingested_at as ingested_at",
    "nullif(review_id, '') as review_id",
    "nullif(order_id, '') as order_id",
    "try_cast(nullif(review_score, '') as int) as review_score",
    "nullif(review_comment_title, '') as review_comment_title",
    "nullif(review_comment_message, '') as review_comment_message",
    "try_cast(nullif(review_creation_date, '') as timestamp) as review_created_at",
    "try_cast(nullif(review_answer_timestamp, '') as timestamp) as review_answered_at",
)
latest_review = Window.partitionBy("review_id").orderBy(
    F.col("review_answered_at").desc_nulls_last(),
    F.col("ingested_at").desc(),
    F.col("source_row_hash"),
)
order_reviews = (
    review_versions.withColumn("review_version", F.row_number().over(latest_review))
    .filter(F.col("review_version") == 1)
    .drop("review_version")
)
write_silver("order_reviews", order_reviews)

customers = bronze("olist_customers").selectExpr(
    "_row_hash as source_row_hash",
    "_batch_date as batch_date",
    "_ingested_at as ingested_at",
    "nullif(customer_id, '') as customer_id",
    "nullif(customer_unique_id, '') as customer_unique_id",
    "try_cast(nullif(customer_zip_code_prefix, '') as int) as zip_code_prefix",
    "nullif(customer_city, '') as customer_city",
    "nullif(customer_state, '') as customer_state",
)
write_silver("customers", customers)

products = bronze("olist_products").selectExpr(
    "_row_hash as source_row_hash",
    "_batch_date as batch_date",
    "_ingested_at as ingested_at",
    "nullif(product_id, '') as product_id",
    "nullif(product_category_name, '') as product_category_name",
    "try_cast(nullif(product_name_lenght, '') as int) as product_name_length",
    "try_cast(nullif(product_description_lenght, '') as int) as product_description_length",
    "try_cast(nullif(product_photos_qty, '') as int) as product_photos_quantity",
    "try_cast(nullif(product_weight_g, '') as decimal(12, 2)) as product_weight_g",
    "try_cast(nullif(product_length_cm, '') as decimal(12, 2)) as product_length_cm",
    "try_cast(nullif(product_height_cm, '') as decimal(12, 2)) as product_height_cm",
    "try_cast(nullif(product_width_cm, '') as decimal(12, 2)) as product_width_cm",
)
write_silver("products", products)

sellers = bronze("olist_sellers").selectExpr(
    "_row_hash as source_row_hash",
    "_batch_date as batch_date",
    "_ingested_at as ingested_at",
    "nullif(seller_id, '') as seller_id",
    "try_cast(nullif(seller_zip_code_prefix, '') as int) as zip_code_prefix",
    "nullif(seller_city, '') as seller_city",
    "nullif(seller_state, '') as seller_state",
)
write_silver("sellers", sellers)

geolocation = (
    bronze("olist_geolocation")
    .selectExpr(
        "try_cast(nullif(geolocation_zip_code_prefix, '') as int) as zip_code_prefix",
        "try_cast(nullif(geolocation_lat, '') as decimal(18, 8)) as latitude",
        "try_cast(nullif(geolocation_lng, '') as decimal(18, 8)) as longitude",
        "nullif(geolocation_city, '') as city",
        "nullif(geolocation_state, '') as state",
    )
    .groupBy("zip_code_prefix")
    .agg(
        F.avg("latitude").alias("latitude"),
        F.avg("longitude").alias("longitude"),
        F.max("city").alias("city"),
        F.max("state").alias("state"),
    )
)
write_silver("geolocation", geolocation)

category_translation = bronze("product_category_name_translation").selectExpr(
    "nullif(product_category_name, '') as product_category_name",
    "nullif(product_category_name_english, '') as product_category_name_english",
).dropDuplicates(["product_category_name"])
write_silver("product_category_translation", category_translation)
