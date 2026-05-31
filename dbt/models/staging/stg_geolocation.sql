select
    nullif(geolocation_zip_code_prefix, '')::integer as zip_code_prefix,
    avg(nullif(geolocation_lat, '')::numeric) as latitude,
    avg(nullif(geolocation_lng, '')::numeric) as longitude,
    max(nullif(geolocation_city, '')) as city,
    max(nullif(geolocation_state, '')) as state
from {{ source('olist', 'olist_geolocation') }}
group by nullif(geolocation_zip_code_prefix, '')::integer
