select
    seller_id,
    seller_city,
    seller_state,
    order_count,
    item_count,
    item_subtotal,
    freight_total,
    order_line_total,
    average_item_price,
    average_review_score
from workspace.ecommerce_gold.mart_seller_performance
order by order_line_total desc, seller_id
limit 10
