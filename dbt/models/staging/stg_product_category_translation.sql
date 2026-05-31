select
    _row_hash as source_row_hash,
    _batch_id as batch_id,
    _loaded_at as loaded_at,
    nullif(product_category_name, '') as product_category_name,
    nullif(product_category_name_english, '') as product_category_name_english
from {{ source('olist', 'product_category_name_translation') }}
