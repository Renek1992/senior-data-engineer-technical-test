select
    game_id,
    game_name,
    vertical,
    game_created_at
from {{ ref('stg__games') }}