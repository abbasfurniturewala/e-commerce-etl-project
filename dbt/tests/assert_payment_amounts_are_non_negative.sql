select *
from {{ ref('stg_order_payments') }}
where payment_value < 0
