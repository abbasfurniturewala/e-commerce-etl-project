with seller_items as (
    select
        seller_id,
        count(*) as item_count,
        sum(item_price)::numeric(16, 2) as item_subtotal,
        sum(freight_value)::numeric(16, 2) as freight_total,
        sum(order_line_total)::numeric(16, 2) as order_line_total,
        avg(item_price)::numeric(14, 2) as average_item_price
    from {{ ref('fct_order_items') }}
    group by seller_id
),

seller_orders as (
    select distinct
        items.seller_id,
        orders.order_id,
        orders.order_purchase_date,
        orders.average_review_score
    from {{ ref('fct_order_items') }} as items
    inner join {{ ref('fct_orders') }} as orders
        on items.order_id = orders.order_id
),

seller_order_rollup as (
    select
        seller_id,
        count(*) as order_count,
        min(order_purchase_date) as first_order_date,
        max(order_purchase_date) as last_order_date,
        avg(average_review_score)::numeric(4, 2) as average_review_score
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
from {{ ref('dim_sellers') }} as sellers
inner join seller_items as items
    on sellers.seller_id = items.seller_id
inner join seller_order_rollup as orders
    on sellers.seller_id = orders.seller_id
