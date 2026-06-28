import os
os.environ["POLARS_VERBOSE"] = "1"
import polars as pl
import pyarrow.dataset as pads
import matplotlib.pyplot as plt
import logging

ball_positions_arrow = pads.dataset("~/Documents/SMT-DATA-CHALLENGE-2026/data/ball-positions", format = 'csv', partitioning = ['home_team', 'away_team', 'year', 'day'])
possible_sb_plays_gamestring_ppg = pl.scan_csv("~/Documents/SMT-Data-Challenge-2026/data/created-objects/possible_sb_plays_gamestring_ppg.csv")

logging.info(f"pads initialized, csv loaded.")

#filter_ball_pos
ball_positions_filtered = (
    pl.scan_pyarrow_dataset(ball_positions_arrow)
    .with_columns(
        pl.concat_str(
            pl.col('game_string'),
            pl.col('play_per_game'),
            separator = '_'
        ).alias('game_string_ppg')
    )
    .join(possible_sb_plays_gamestring_ppg, on = 'game_string_ppg', how = 'semi')
    .collect()
)


q = (
    ball_positions_filtered.lazy()
    .group_by("game_string_ppg")
    .agg(
        (pl.col("ball_position_y")).min().alias("min_y_pos"),
        (pl.col("timestamp")).min().alias("t_0"),
        (pl.col("timestamp")).max().alias("max_t")
    )
    .collect()
)

print(q.head())




