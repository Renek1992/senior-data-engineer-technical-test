select
    id as bet_id,
    user_id,
    bet_outcome_id,
    game_id,
    wager,
    winnings,
    is_cash_wager,
    created_at as bet_placed_at,
    settled_at as bet_settled_at
from {{ source('raw', 'bet') }}