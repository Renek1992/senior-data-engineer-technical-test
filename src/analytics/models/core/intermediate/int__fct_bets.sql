with bets as (
    select * from {{ ref('stg_bets') }}
),

users as (
    select user_id, currency_code from {{ ref('dim_user') }}
),

fx_rates as (
    select * from {{ ref('stg_fx_rates') }}
),

-- add fx rate for wager date
bets_with_currency as (
    select
        b.*,
        u.currency_code,
        coalesce(b.settled_at, b.bet_placed_at)::date as fx_date
    from bets b
    left join users u on b.user_id = u.user_id
),

bets_with_fx as (
    select
        b.*,
        fx.rate,
        b.wager * fx.rate as wager_usd,
        b.winnings * fx.rate as winnings_usd
    from bets_with_currency b
    left join fx_rates fx
      on fx.currency_code = b.currency_code
     and fx.date = b.fx_date
)

select
    bet_id,
    user_id,
    game_id,
    bet_outcome_id,
    is_cash_wager,
    wager,
    winnings,
    wager_usd,
    winnings_usd,
    bet_placed_at,
    bet_settled_at
from bets_with_fx