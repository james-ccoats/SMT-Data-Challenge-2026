import polars as pl
import polars.selectors as cs
import os
import pyarrow.dataset as pads

#load in lineups data
lineup_data = pl.read_csv('lineups.csv', null_values="NA")

#create game_string_ppg variable
lineup_data_df = lineup_data.with_columns(
    pl.concat_str(
        pl.col('game_string'),
        pl.col('play_per_game'),
        separator = "_"
    ).alias('game_string_ppg')
)

#we want to find play events where batter is the same, but runner moves from first to second, 
#or runner was on first and is no longer on first.
lineup_data_first_row = lineup_data_df.filter(
    (pl.col('on_1b').is_not_null()) & (pl.col('on_1b').shift(-1).is_null()) & (pl.col('batter') == pl.col('batter').shift(-1))
)

lineup_data_second_row= lineup_data_df.filter(
    (pl.col('on_1b').is_null()) & (pl.col('on_1b').shift(1).is_not_null()) & (pl.col('batter') == pl.col('batter').shift(1))
)

#combine possible stolen base attempts into one dataframe
possible_sb_plays = pl.concat([lineup_data_first_row, lineup_data_second_row])

#order the plays of possible_sb_plays
possible_sb_plays_ordered = possible_sb_plays.sort('game_string', 'play_per_game')

#remove pickoff plays
possible_sb_plays = possible_sb_plays_ordered.filter(
    pl.col('is_pickoff') == 'false'
)
