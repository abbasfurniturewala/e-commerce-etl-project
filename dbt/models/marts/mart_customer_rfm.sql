with customer_orders as (
    select
        customers.customer_unique_id,
        orders.order_id,
        orders.order_purchase_date,
        orders.payment_total
    from {{ ref('fct_orders') }} as orders
    inner join {{ ref('dim_customers') }} as customers
        on orders.customer_id = customers.customer_id
),

reference_date as (
    select max(order_purchase_date) + 1 as snapshot_date
    from customer_orders
),

rfm_metrics as (
    select
        customer_orders.customer_unique_id,
        reference_date.snapshot_date,
        max(customer_orders.order_purchase_date) as last_order_date,
        (
            reference_date.snapshot_date - max(customer_orders.order_purchase_date)
        )::integer as recency_days,
        count(distinct customer_orders.order_id) as order_count,
        sum(customer_orders.payment_total)::numeric(16, 2) as monetary_value,
        avg(customer_orders.payment_total)::numeric(14, 2) as average_order_value
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
