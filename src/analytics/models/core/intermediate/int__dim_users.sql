with users as (
    select * from {{ ref('stg__users') }}
),

addresses as (
    select * from {{ ref('stg__user_address') }}
)

select
    u.user_id,
    u.user_name,
    a.country_code,
    u.currency_code,
    u.user_created_at
from users u
left join addresses a on u.user_id = a.user_id