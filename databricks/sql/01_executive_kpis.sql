select
    count(*) as total_orders,
    count(distinct customer_id) as total_customers,
    sum(item_count) as total_items,
    cast(sum(payment_total) as decimal(16, 2)) as gross_payment_value,
    cast(avg(payment_total) as decimal(14, 2)) as average_order_value,
    cast(avg(average_review_score) as decimal(4, 2)) as average_review_score
from workspace.ecommerce_gold.fct_orders
