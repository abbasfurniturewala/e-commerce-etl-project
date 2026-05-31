with segmented_customers as (
    select
        customer_unique_id,
        monetary_value,
        average_order_value,
        case
            when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4
                then 'Champions'
            when recency_score >= 3 and frequency_score >= 3
                then 'Loyal customers'
            when recency_score >= 4
                then 'Recent customers'
            when recency_score <= 2 and frequency_score >= 3
                then 'At risk'
            else 'Needs attention'
        end as customer_segment
    from workspace.ecommerce_gold.mart_customer_rfm
)
select
    customer_segment,
    count(*) as customer_count,
    cast(sum(monetary_value) as decimal(16, 2)) as segment_value,
    cast(avg(average_order_value) as decimal(14, 2)) as average_order_value
from segmented_customers
group by customer_segment
order by segment_value desc, customer_segment
