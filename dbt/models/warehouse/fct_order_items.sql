select
    items.order_item_sk,
    items.order_id,
    orders.order_purchase_at::date as order_purchase_date,
    items.order_item_id,
    items.product_id,
    items.seller_id,
    items.shipping_limit_at,
    items.item_price,
    items.freight_value,
    (items.item_price + items.freight_value)::numeric(14, 2) as order_line_total
from {{ ref('stg_order_items') }} as items
inner join {{ ref('stg_orders') }} as orders
    on items.order_id = orders.order_id
