select *
from {{ ref('stg_order_items') }}
where item_price < 0
   or freight_value < 0
