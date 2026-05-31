CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.ingestion_runs (
    batch_id text PRIMARY KEY,
    batch_date date NOT NULL,
    status text NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    row_counts jsonb,
    error_message text
);

CREATE TABLE IF NOT EXISTS raw.ingested_files (
    batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    table_name text NOT NULL,
    source_file text NOT NULL,
    sha256 text NOT NULL UNIQUE,
    row_count integer NOT NULL,
    inserted_row_count integer NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE raw.ingested_files
ADD COLUMN IF NOT EXISTS inserted_row_count integer NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS raw.olist_orders (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    order_id text,
    customer_id text,
    order_status text,
    order_purchase_timestamp text,
    order_approved_at text,
    order_delivered_carrier_date text,
    order_delivered_customer_date text,
    order_estimated_delivery_date text
);

CREATE TABLE IF NOT EXISTS raw.olist_order_items (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    order_id text,
    order_item_id text,
    product_id text,
    seller_id text,
    shipping_limit_date text,
    price text,
    freight_value text
);

CREATE TABLE IF NOT EXISTS raw.olist_order_payments (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    order_id text,
    payment_sequential text,
    payment_type text,
    payment_installments text,
    payment_value text
);

CREATE TABLE IF NOT EXISTS raw.olist_order_reviews (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    review_id text,
    order_id text,
    review_score text,
    review_comment_title text,
    review_comment_message text,
    review_creation_date text,
    review_answer_timestamp text
);

CREATE TABLE IF NOT EXISTS raw.olist_customers (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    customer_id text,
    customer_unique_id text,
    customer_zip_code_prefix text,
    customer_city text,
    customer_state text
);

CREATE TABLE IF NOT EXISTS raw.olist_products (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    product_id text,
    product_category_name text,
    product_name_lenght text,
    product_description_lenght text,
    product_photos_qty text,
    product_weight_g text,
    product_length_cm text,
    product_height_cm text,
    product_width_cm text
);

CREATE TABLE IF NOT EXISTS raw.olist_sellers (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    seller_id text,
    seller_zip_code_prefix text,
    seller_city text,
    seller_state text
);

CREATE TABLE IF NOT EXISTS raw.olist_geolocation (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    geolocation_zip_code_prefix text,
    geolocation_lat text,
    geolocation_lng text,
    geolocation_city text,
    geolocation_state text
);

CREATE TABLE IF NOT EXISTS raw.product_category_name_translation (
    _row_hash text PRIMARY KEY,
    _batch_id text NOT NULL REFERENCES raw.ingestion_runs(batch_id),
    _source_file text NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now(),
    product_category_name text,
    product_category_name_english text
);
