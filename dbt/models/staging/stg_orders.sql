select
    _row_hash as source_row_hash,
    _batch_id as batch_id,
    _loaded_at as loaded_at,
    nullif(order_id, '') as order_id,
    nullif(customer_id, '') as customer_id,
    nullif(order_status, '') as order_status,
    nullif(order_purchase_timestamp, '')::timestamp as order_purchase_at,
    nullif(order_approved_at, '')::timestamp as order_approved_at,
    nullif(order_delivered_carrier_date, '')::timestamp as order_delivered_carrier_at,
    nullif(order_delivered_customer_date, '')::timestamp as order_delivered_customer_at,
    nullif(order_estimated_delivery_date, '')::timestamp as order_estimated_delivery_at
from {{ source('olist', 'olist_orders') }}
