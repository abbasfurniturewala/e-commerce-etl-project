select
    zip_code_prefix,
    latitude,
    longitude,
    city,
    state
from {{ ref('stg_geolocation') }}
