from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dataset:
    filename: str
    table_name: str
    columns: tuple[str, ...]


DATASETS = (
    Dataset(
        "olist_orders_dataset.csv",
        "olist_orders",
        (
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
    ),
    Dataset(
        "olist_order_items_dataset.csv",
        "olist_order_items",
        (
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ),
    ),
    Dataset(
        "olist_order_payments_dataset.csv",
        "olist_order_payments",
        (
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ),
    ),
    Dataset(
        "olist_order_reviews_dataset.csv",
        "olist_order_reviews",
        (
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ),
    ),
    Dataset(
        "olist_customers_dataset.csv",
        "olist_customers",
        (
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
    ),
    Dataset(
        "olist_products_dataset.csv",
        "olist_products",
        (
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
    ),
    Dataset(
        "olist_sellers_dataset.csv",
        "olist_sellers",
        (
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ),
    ),
    Dataset(
        "olist_geolocation_dataset.csv",
        "olist_geolocation",
        (
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ),
    ),
    Dataset(
        "product_category_name_translation.csv",
        "product_category_name_translation",
        (
            "product_category_name",
            "product_category_name_english",
        ),
    ),
)

DATASETS_BY_FILENAME = {dataset.filename: dataset for dataset in DATASETS}
