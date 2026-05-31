select
    _row_hash as source_row_hash,
    _batch_id as batch_id,
    _loaded_at as loaded_at,
    nullif(seller_id, '') as seller_id,
    nullif(seller_zip_code_prefix, '')::integer as zip_code_prefix,
    nullif(seller_city, '') as seller_city,
    nullif(seller_state, '') as seller_state
from {{ source('olist', 'olist_sellers') }}
