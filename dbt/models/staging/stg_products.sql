select
    _row_hash as source_row_hash,
    _batch_id as batch_id,
    _loaded_at as loaded_at,
    nullif(product_id, '') as product_id,
    nullif(product_category_name, '') as product_category_name,
    nullif(product_name_lenght, '')::integer as product_name_length,
    nullif(product_description_lenght, '')::integer as product_description_length,
    nullif(product_photos_qty, '')::integer as product_photos_quantity,
    nullif(product_weight_g, '')::numeric(12, 2) as product_weight_g,
    nullif(product_length_cm, '')::numeric(12, 2) as product_length_cm,
    nullif(product_height_cm, '')::numeric(12, 2) as product_height_cm,
    nullif(product_width_cm, '')::numeric(12, 2) as product_width_cm
from {{ source('olist', 'olist_products') }}
