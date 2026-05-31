select
    order_purchase_date,
    count(*) as order_count,
    sum(item_count) as item_count,
    sum(item_subtotal)::numeric(16, 2) as item_subtotal,
    sum(freight_total)::numeric(16, 2) as freight_total,
    sum(order_line_total)::numeric(16, 2) as order_line_total,
    sum(payment_total)::numeric(16, 2) as payment_total,
    avg(average_review_score)::numeric(4, 2) as average_review_score
from {{ ref('fct_orders') }}
group by order_purchase_date
