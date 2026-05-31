# Databricks notebook source
def widget(name: str, default: str) -> str:
    dbutils.widgets.text(name, default)
    return dbutils.widgets.get(name)


def quoted(identifier: str) -> str:
    return f"`{identifier.replace('`', '``')}`"


catalog = widget("catalog", "") or spark.sql("select current_catalog()").first()[0]
silver_schema = widget("silver_schema", "ecommerce_silver")
gold_schema = widget("gold_schema", "ecommerce_gold")


def silver(table_name: str) -> str:
    return f"{quoted(catalog)}.{quoted(silver_schema)}.{quoted(table_name)}"


def gold(table_name: str) -> str:
    return f"{quoted(catalog)}.{quoted(gold_schema)}.{quoted(table_name)}"


def replace_table(table_name: str, select_statement: str) -> None:
    spark.sql(
        f"""
        create or replace table {gold(table_name)}
        using delta
        as {select_statement}
        """
    )
    print(f"{gold(table_name)}: {spark.table(f'{catalog}.{gold_schema}.{table_name}').count()} Gold rows")


spark.sql(f"create schema if not exists {quoted(catalog)}.{quoted(gold_schema)}")

replace_table(
    "dim_customers",
    f"""
    select customer_id, customer_unique_id, zip_code_prefix, customer_city, customer_state
    from {silver("customers")}
    """,
)
replace_table(
    "dim_products",
    f"""
    select
        products.product_id,
        products.product_category_name,
        coalesce(
            categories.product_category_name_english,
            products.product_category_name,
            'unknown'
        ) as product_category_name_english,
        products.product_name_length,
        products.product_description_length,
        products.product_photos_quantity,
        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm
    from {silver("products")} as products
    left join {silver("product_category_translation")} as categories
        on products.product_category_name = categories.product_category_name
    """,
)

replace_table(
    "dim_sellers",
    f"""
    select seller_id, zip_code_prefix, seller_city, seller_state
    from {silver("sellers")}
    """,
)

replace_table(
    "dim_geography",
    f"""
    select zip_code_prefix, latitude, longitude, city, state
    from {silver("geolocation")}
    """,
)

replace_table(
    "dim_date",
    f"""
    with date_bounds as (
        select
            min(to_date(order_purchase_at)) as start_date,
            greatest(
                max(to_date(order_purchase_at)),
                max(to_date(order_estimated_delivery_at))
            ) as end_date
        from {silver("orders")}
    ),
    date_spine as (
        select explode(sequence(start_date, end_date, interval 1 day)) as date_day
        from date_bounds
    )
    select
        cast(date_format(date_day, 'yyyyMMdd') as int) as date_key,
        date_day,
        year(date_day) as year_number,
        quarter(date_day) as quarter_number,
        month(date_day) as month_number,
        date_format(date_day, 'MMMM') as month_name,
        weekofyear(date_day) as week_number,
        dayofweek(date_day) as day_of_week_number,
        date_format(date_day, 'EEEE') as day_of_week_name,
        dayofweek(date_day) in (1, 7) as is_weekend
    from date_spine
    """,
)

replace_table(
    "fct_orders",
    f"""
    with item_rollup as (
        select
            order_id,
            count(*) as item_count,
            count(distinct product_id) as distinct_product_count,
            count(distinct seller_id) as distinct_seller_count,
            sum(item_price) as item_subtotal,
            sum(freight_value) as freight_total,
            sum(item_price + freight_value) as order_line_total
        from {silver("order_items")}
        group by order_id
    ),
    payment_rollup as (
        select
            order_id,
            count(*) as payment_count,
            sum(payment_value) as payment_total
        from {silver("order_payments")}
        group by order_id
    ),
    review_rollup as (
        select
            order_id,
            count(*) as review_count,
            cast(avg(review_score) as decimal(4, 2)) as average_review_score
        from {silver("order_reviews")}
        group by order_id
    )
    select
        orders.order_id,
        orders.customer_id,
        orders.order_status,
        to_date(orders.order_purchase_at) as order_purchase_date,
        orders.order_purchase_at,
        orders.order_approved_at,
        orders.order_delivered_carrier_at,
        orders.order_delivered_customer_at,
        orders.order_estimated_delivery_at,
        coalesce(items.item_count, 0) as item_count,
        coalesce(items.distinct_product_count, 0) as distinct_product_count,
        coalesce(items.distinct_seller_count, 0) as distinct_seller_count,
        cast(coalesce(items.item_subtotal, 0) as decimal(14, 2)) as item_subtotal,
        cast(coalesce(items.freight_total, 0) as decimal(14, 2)) as freight_total,
        cast(coalesce(items.order_line_total, 0) as decimal(14, 2)) as order_line_total,
        coalesce(payments.payment_count, 0) as payment_count,
        cast(coalesce(payments.payment_total, 0) as decimal(14, 2)) as payment_total,
        coalesce(reviews.review_count, 0) as review_count,
        reviews.average_review_score
    from {silver("orders")} as orders
    left join item_rollup as items on orders.order_id = items.order_id
    left join payment_rollup as payments on orders.order_id = payments.order_id
    left join review_rollup as reviews on orders.order_id = reviews.order_id
    """,
)

replace_table(
    "fct_order_items",
    f"""
    select
        items.order_item_sk,
        items.order_id,
        to_date(orders.order_purchase_at) as order_purchase_date,
        items.order_item_id,
        items.product_id,
        items.seller_id,
        items.shipping_limit_at,
        items.item_price,
        items.freight_value,
        cast(items.item_price + items.freight_value as decimal(14, 2)) as order_line_total
    from {silver("order_items")} as items
    inner join {silver("orders")} as orders on items.order_id = orders.order_id
    """,
)

replace_table(
    "mart_daily_sales",
    f"""
    select
        order_purchase_date,
        count(*) as order_count,
        sum(item_count) as item_count,
        cast(sum(item_subtotal) as decimal(16, 2)) as item_subtotal,
        cast(sum(freight_total) as decimal(16, 2)) as freight_total,
        cast(sum(order_line_total) as decimal(16, 2)) as order_line_total,
        cast(sum(payment_total) as decimal(16, 2)) as payment_total,
        cast(avg(average_review_score) as decimal(4, 2)) as average_review_score
    from {gold("fct_orders")}
    group by order_purchase_date
    """,
)

replace_table(
    "mart_delivery_performance",
    f"""
    select
        order_purchase_date,
        count(*) as order_count,
        sum(case when order_delivered_customer_at is not null then 1 else 0 end) as delivered_order_count,
        sum(
            case when order_delivered_customer_at > order_estimated_delivery_at then 1 else 0 end
        ) as late_delivery_count,
        cast(
            sum(case when order_delivered_customer_at > order_estimated_delivery_at then 1 else 0 end)
            / nullif(sum(case when order_delivered_customer_at is not null then 1 else 0 end), 0)
            as decimal(8, 4)
        ) as late_delivery_rate,
        cast(avg(datediff(order_delivered_customer_at, order_purchase_at)) as decimal(10, 2))
            as average_delivery_days,
        cast(avg(datediff(order_delivered_customer_at, order_estimated_delivery_at)) as decimal(10, 2))
            as average_days_vs_estimate
    from {gold("fct_orders")}
    group by order_purchase_date
    """,
)

replace_table(
    "mart_seller_performance",
    f"""
    with seller_items as (
        select
            seller_id,
            count(*) as item_count,
            cast(sum(item_price) as decimal(16, 2)) as item_subtotal,
            cast(sum(freight_value) as decimal(16, 2)) as freight_total,
            cast(sum(order_line_total) as decimal(16, 2)) as order_line_total,
            cast(avg(item_price) as decimal(14, 2)) as average_item_price
        from {gold("fct_order_items")}
        group by seller_id
    ),
    seller_orders as (
        select distinct
            items.seller_id,
            orders.order_id,
            orders.order_purchase_date,
            orders.average_review_score
        from {gold("fct_order_items")} as items
        inner join {gold("fct_orders")} as orders on items.order_id = orders.order_id
    ),
    seller_order_rollup as (
        select
            seller_id,
            count(*) as order_count,
            min(order_purchase_date) as first_order_date,
            max(order_purchase_date) as last_order_date,
            cast(avg(average_review_score) as decimal(4, 2)) as average_review_score
        from seller_orders
        group by seller_id
    )
    select
        sellers.seller_id,
        sellers.seller_city,
        sellers.seller_state,
        sellers.zip_code_prefix,
        orders.order_count,
        items.item_count,
        items.item_subtotal,
        items.freight_total,
        items.order_line_total,
        items.average_item_price,
        orders.average_review_score,
        orders.first_order_date,
        orders.last_order_date
    from {gold("dim_sellers")} as sellers
    inner join seller_items as items on sellers.seller_id = items.seller_id
    inner join seller_order_rollup as orders on sellers.seller_id = orders.seller_id
    """,
)

replace_table(
    "mart_customer_rfm",
    f"""
    with customer_orders as (
        select
            customers.customer_unique_id,
            orders.order_id,
            orders.order_purchase_date,
            orders.payment_total
        from {gold("fct_orders")} as orders
        inner join {gold("dim_customers")} as customers on orders.customer_id = customers.customer_id
    ),
    reference_date as (
        select date_add(max(order_purchase_date), 1) as snapshot_date
        from customer_orders
    ),
    rfm_metrics as (
        select
            customer_orders.customer_unique_id,
            reference_date.snapshot_date,
            max(customer_orders.order_purchase_date) as last_order_date,
            datediff(reference_date.snapshot_date, max(customer_orders.order_purchase_date)) as recency_days,
            count(distinct customer_orders.order_id) as order_count,
            cast(sum(customer_orders.payment_total) as decimal(16, 2)) as monetary_value,
            cast(avg(customer_orders.payment_total) as decimal(14, 2)) as average_order_value
        from customer_orders
        cross join reference_date
        group by customer_orders.customer_unique_id, reference_date.snapshot_date
    ),
    rfm_scores as (
        select
            *,
            6 - ntile(5) over (order by recency_days) as recency_score,
            ntile(5) over (order by order_count) as frequency_score,
            ntile(5) over (order by monetary_value) as monetary_score
        from rfm_metrics
    )
    select
        *,
        concat(recency_score, frequency_score, monetary_score) as rfm_score
    from rfm_scores
    """,
)
