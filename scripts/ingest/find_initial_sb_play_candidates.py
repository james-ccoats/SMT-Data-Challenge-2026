import polars as pl
import polars.selectors as cs
import os
import pyarrow.dataset as pads

####################################################
### Code Taken from SMT_Data_Starter
####################################################

# For the data_path argument, include the full file path to the folder that holds the data!    
def readDataSubset(table_type, data_path="/Users/jamesccoats/Documents/SMT-Data-Challenge-2026/data"):
    '''
    Takes a the set of tables from Data set and
    transforms into panda data frame for manipulation
    
    Input:
    -     table_type   = Set of tables of interest from Data set [str]
    -     data_path    = File Path which data is located in Local device, change as necessary[str]
    
    '''
    if table_type not in ['ball-positions', 'ball-events', 'player-positions', 'lineups', 'game-info']:
        print("Invalid data subset name. Please try again with a valid data subset.")
        return -1

    if table_type == 'lineups' or table_type == 'game-info':
        return pads.dataset(source = os.path.join(os.path.dirname(__name__), data_path, table_type + '.csv'), format = 'csv')
    else:
        return pads.dataset(source = os.path.join(os.path.dirname(__name__), data_path, table_type), format = 'csv', partitioning = ['home_team', 'away_team', 'year', 'day'])
    
#load in lineups data
lineup_data = pl.read_csv('data/lineups.csv', null_values="NA")

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

#get unique game strings of the possible stolen base plays
possible_sb_plays_gamestring_ppg = possible_sb_plays['game_string_ppg'].unique().to_list()

#we need to filter passed ball events, since they are not stolen bases. We will join ball-positions and filter where the ball
#doesnt go behind the catcher for the duration of the play. 
ball_positions_arrow = pads.dataset("~/Documents/SMT-DATA-CHALLENGE-2026/data/ball-positions", format = 'csv')
ball_positions_filtered = (
    pl.scan_pyarrow_dataset(ball_positions_arrow)
    .filter(pl.col('game_string').is_in(possible_sb_plays_gamestring_ppg))
    .collect()
)

possible_sb_plays_gamestring_ppg = pl.DataFrame(possible_sb_plays_gamestring_ppg, schema = ['game_string_ppg'])

possible_sb_plays_gamestring_ppg.write_csv("data/created-objects/possible_sb_plays_gamestring_ppg.csv")
ball_positions_filtered.write_csv("data/created-objects/ball_positions_filtered.csv")
