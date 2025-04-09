with source as (
    select * from {{ source('raw', 'users') }}
),

renamed as (
    select
        id as user_id,
        lower(trim(name)) as user_name,
        is_test_user,
        upper(currency_code) as currency_code,
        created_at as user_created_at
    from source
    where not is_test_user  -- remove internal test accounts
)

select * from renamed