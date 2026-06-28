import os
os.environ["POLARS_VERBOSE"] = "1"
import polars as pl
import pyarrow.dataset as pads
import matplotlib.pyplot as plt
import logging
from plotnine import *

#the purpose of this script is to figure out the standard coordinates of the catcher when he is behind the plate.
#we can just use another subset of the data for ease of calculations since catcher positoning is pretty standard.

#set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info(f"Initializing")

#set up PADS
player_positions_arrow = pads.dataset("~/Documents/SMT-Data-Challenge-2026/data/player-positions", format = 'csv', partitioning = ['home_team', 'away_team', 'year', 'day'])
possible_sb_plays_gamestring_ppg = pl.scan_csv("~/Documents/SMT-Data-Challenge-2026/data/created-objects/possible_sb_plays_gamestring_ppg.csv")

logger.info(f"pads iniialized and lazyframe loaded.")

#import
player_position_sample = (
    pl.scan_pyarrow_dataset(player_positions_arrow)
    .filter(pl.col('player_id') == 2)
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

logger.info(f"Scan complete. Loaded {player_position_sample.height} rows.")

player_position_sample.write_csv('data/created-objects/player_positions_sample.csv')

logger.info(f'Saved Player Positions to CSV')

plot = (
    ggplot(data = player_position_sample, mapping = aes(x = "field_y"))
    +geom_density(color = "#03bafc", fill = "#03bafc", alpha = 0.8)
    +labs(x = "Catcher y Position", y = "Density", title = "Catcher Y Coordinate Distribution")
    +theme_minimal()
)

save_path = os.path.expanduser('~/Documents/SMT-Data-Challenge-2026/viz/catcher_positioning_distribution.png')
plot.save(save_path, width=8, height=6, dpi = 600)

#based on the density plot, we will assume that any time the ball gets past -8, it is a passed ball and not a stolen base play.
