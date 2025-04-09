select
    id as bet_outcome_id,
    lower(outcome) as outcome
from {{ source('raw', 'bet_outcome') }}