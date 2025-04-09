select
    date,
    upper(currency_code) as currency_code,
    rate
from {{ source('raw', 'fx_rates') }}