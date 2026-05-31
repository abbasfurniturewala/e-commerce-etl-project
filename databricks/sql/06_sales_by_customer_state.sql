select
    customers.customer_state,
    count(*) as order_count,
    count(distinct orders.customer_id) as customer_count,
    cast(sum(orders.payment_total) as decimal(16, 2)) as gross_payment_value,
    cast(avg(orders.payment_total) as decimal(14, 2)) as average_order_value
from workspace.ecommerce_gold.fct_orders as orders
inner join workspace.ecommerce_gold.dim_customers as customers
    on orders.customer_id = customers.customer_id
group by customers.customer_state
order by gross_payment_value desc, customers.customer_state
