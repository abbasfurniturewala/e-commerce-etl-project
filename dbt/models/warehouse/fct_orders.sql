with item_rollup as (
    select
        order_id,
        count(*) as item_count,
        count(distinct product_id) as distinct_product_count,
        count(distinct seller_id) as distinct_seller_count,
        sum(item_price) as item_subtotal,
        sum(freight_value) as freight_total,
        sum(item_price + freight_value) as order_line_total
    from {{ ref('stg_order_items') }}
    group by order_id
),

payment_rollup as (
    select
        order_id,
        count(*) as payment_count,
        sum(payment_value) as payment_total
    from {{ ref('stg_order_payments') }}
    group by order_id
),

review_rollup as (
    select
        order_id,
        count(*) as review_count,
        avg(review_score)::numeric(4, 2) as average_review_score
    from {{ ref('stg_order_reviews') }}
    group by order_id
)

select
    orders.order_id,
    orders.customer_id,
    orders.order_status,
    orders.order_purchase_at::date as order_purchase_date,
    orders.order_purchase_at,
    orders.order_approved_at,
    orders.order_delivered_carrier_at,
    orders.order_delivered_customer_at,
    orders.order_estimated_delivery_at,
    coalesce(items.item_count, 0) as item_count,
    coalesce(items.distinct_product_count, 0) as distinct_product_count,
    coalesce(items.distinct_seller_count, 0) as distinct_seller_count,
    coalesce(items.item_subtotal, 0)::numeric(14, 2) as item_subtotal,
    coalesce(items.freight_total, 0)::numeric(14, 2) as freight_total,
    coalesce(items.order_line_total, 0)::numeric(14, 2) as order_line_total,
    coalesce(payments.payment_count, 0) as payment_count,
    coalesce(payments.payment_total, 0)::numeric(14, 2) as payment_total,
    coalesce(reviews.review_count, 0) as review_count,
    reviews.average_review_score
from {{ ref('stg_orders') }} as orders
left join item_rollup as items
    on orders.order_id = items.order_id
left join payment_rollup as payments
    on orders.order_id = payments.order_id
left join review_rollup as reviews
    on orders.order_id = reviews.order_id
