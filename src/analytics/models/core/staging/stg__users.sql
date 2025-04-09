with source as (
    select * from {{ source('raw', 'users') }}
),

renamed as (
    select
        id as user_id,
        lower(trim("Name")) as user_name,           -- quoted correctly
        "IsTestUser" as is_test_user,               -- quoted correctly
        upper("CurrencyCode") as currency_code,     -- quoted correctly
        "CreatedAt" as user_created_at              -- quoted correctly
    from source
    where not "IsTestUser"  -- also fix here
)

select * from renamed