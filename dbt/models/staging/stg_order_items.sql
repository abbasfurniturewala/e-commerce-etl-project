select
    md5(concat_ws('||', order_id, order_item_id)) as order_item_sk,
    _row_hash as source_row_hash,
    _batch_id as batch_id,
    _loaded_at as loaded_at,
    nullif(order_id, '') as order_id,
    nullif(order_item_id, '')::integer as order_item_id,
    nullif(product_id, '') as product_id,
    nullif(seller_id, '') as seller_id,
    nullif(shipping_limit_date, '')::timestamp as shipping_limit_at,
    nullif(price, '')::numeric(12, 2) as item_price,
    nullif(freight_value, '')::numeric(12, 2) as freight_value
from {{ source('olist', 'olist_order_items') }}
