with date_bounds as (
    select
        min(order_purchase_at::date) as start_date,
        greatest(
            max(order_purchase_at::date),
            max(order_estimated_delivery_at::date)
        ) as end_date
    from {{ ref('stg_orders') }}
),

date_spine as (
    select generate_series(start_date, end_date, interval '1 day')::date as date_day
    from date_bounds
)

select
    to_char(date_day, 'YYYYMMDD')::integer as date_key,
    date_day,
    extract(year from date_day)::integer as year_number,
    extract(quarter from date_day)::integer as quarter_number,
    extract(month from date_day)::integer as month_number,
    to_char(date_day, 'Month') as month_name,
    extract(week from date_day)::integer as week_number,
    extract(isodow from date_day)::integer as day_of_week_number,
    to_char(date_day, 'Day') as day_of_week_name,
    extract(isodow from date_day) in (6, 7) as is_weekend
from date_spine
