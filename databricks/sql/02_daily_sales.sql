select
    order_purchase_date,
    order_count,
    item_count,
    item_subtotal,
    freight_total,
    order_line_total,
    payment_total,
    average_review_score
from workspace.ecommerce_gold.mart_daily_sales
order by order_purchase_date
