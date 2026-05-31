with typed_reviews as (
    select
        _row_hash as source_row_hash,
        _batch_id as batch_id,
        _loaded_at as loaded_at,
        nullif(review_id, '') as review_id,
        nullif(order_id, '') as order_id,
        nullif(review_score, '')::integer as review_score,
        nullif(review_comment_title, '') as review_comment_title,
        nullif(review_comment_message, '') as review_comment_message,
        nullif(review_creation_date, '')::timestamp as review_created_at,
        nullif(review_answer_timestamp, '')::timestamp as review_answered_at
    from {{ source('olist', 'olist_order_reviews') }}
),

ranked_reviews as (
    select
        *,
        row_number() over (
            partition by review_id
            order by review_answered_at desc nulls last, loaded_at desc, source_row_hash
        ) as review_version
    from typed_reviews
)

select
    source_row_hash,
    batch_id,
    loaded_at,
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_created_at,
    review_answered_at
from ranked_reviews
where review_version = 1
