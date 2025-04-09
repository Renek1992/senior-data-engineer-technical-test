select
    game_id,
    game_name,
    vertical,
    game_created_at
from {{ ref('stg_games') }}