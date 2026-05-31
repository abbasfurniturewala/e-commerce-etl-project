select
    order_purchase_date,
    order_count,
    delivered_order_count,
    late_delivery_count,
    cast(100 * late_delivery_rate as decimal(8, 2)) as late_delivery_percentage,
    average_delivery_days,
    average_days_vs_estimate
from workspace.ecommerce_gold.mart_delivery_performance
order by order_purchase_date
