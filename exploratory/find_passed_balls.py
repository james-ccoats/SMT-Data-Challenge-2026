import polars as pl
import pyarrow.dataset as pads
import matplotlib.pyplot as plt
from create_stolen_base_df import possible_sb_plays_gamestring_ppg

ball_positions_arrow = pads.dataset("~/Documents/SMT-DATA-CHALLENGE-2026/ball-positions", format = 'csv')

ball_positions_filtered = (
    pl.scan_pyarrow_dataset(ball_positions_arrow)
    .filter(pl.col('game_string').is_in(possible_sb_plays_gamestring_ppg))
    .with_columns(
        pl.concat_str(
            pl.col('game_string'),
            pl.col('play_per_game'),
            separator = '_'
        ).alias('game_string_ppg')
    )
    .filter(pl.col('game_string_ppg')=='y1_d145_ADQ_ANI_1')
    .collect()
)

timestamp = ball_positions_filtered['timestamp']
ball_pos_y = ball_positions_filtered['ball_position_y']

plt.plot(timestamp, ball_pos_y)
plt.show()