select
    order_purchase_date,
    count(*) as order_count,
    count(*) filter (
        where order_delivered_customer_at is not null
    ) as delivered_order_count,
    count(*) filter (
        where order_delivered_customer_at > order_estimated_delivery_at
    ) as late_delivery_count,
    (
        count(*) filter (
            where order_delivered_customer_at > order_estimated_delivery_at
        )::numeric
        / nullif(
            count(*) filter (
                where order_delivered_customer_at is not null
            ),
            0
        )
    )::numeric(8, 4) as late_delivery_rate,
    avg(
        extract(epoch from (order_delivered_customer_at - order_purchase_at)) / 86400
    )::numeric(10, 2) as average_delivery_days,
    avg(
        extract(epoch from (order_delivered_customer_at - order_estimated_delivery_at)) / 86400
    )::numeric(10, 2) as average_days_vs_estimate
from {{ ref('fct_orders') }}
group by order_purchase_date
