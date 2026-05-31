select
    _row_hash as source_row_hash,
    _batch_id as batch_id,
    _loaded_at as loaded_at,
    nullif(customer_id, '') as customer_id,
    nullif(customer_unique_id, '') as customer_unique_id,
    nullif(customer_zip_code_prefix, '')::integer as zip_code_prefix,
    nullif(customer_city, '') as customer_city,
    nullif(customer_state, '') as customer_state
from {{ source('olist', 'olist_customers') }}
