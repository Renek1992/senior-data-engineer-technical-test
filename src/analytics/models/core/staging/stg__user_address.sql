with source as (
    select * from {{ source('raw', 'user_address') }}
),

filtered as (
    select *
    from source
    where country_code in ('IE', 'GB')  -- remove any out-of-scope countries
)

select
    user_id,
    address,
    country_code
from filtered