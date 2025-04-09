select
    id as game_id,
    lower(name) as game_name,
    lower(vertical) as vertical,
    created_at as game_created_at
from {{ source('raw', 'game') }}