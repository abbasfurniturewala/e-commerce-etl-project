select
    seller_id,
    zip_code_prefix,
    seller_city,
    seller_state
from {{ ref('stg_sellers') }}
