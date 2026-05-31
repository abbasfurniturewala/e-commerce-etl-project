select
    md5(concat_ws('||', order_id, payment_sequential)) as payment_sk,
    _row_hash as source_row_hash,
    _batch_id as batch_id,
    _loaded_at as loaded_at,
    nullif(order_id, '') as order_id,
    nullif(payment_sequential, '')::integer as payment_sequence,
    nullif(payment_type, '') as payment_type,
    nullif(payment_installments, '')::integer as payment_installments,
    nullif(payment_value, '')::numeric(12, 2) as payment_value
from {{ source('olist', 'olist_order_payments') }}
