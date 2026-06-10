import pandas as pd
from itertools import permutations

def get_teams(fixtures):
    return pd.concat(
        [fixtures["home_team"], fixtures["away_team"]]
    ).drop_duplicates().tolist()



def build_predicted_goals_lookup(teams, model): 
    df = pd.DataFrame(
            permutations(teams, 2), 
            columns=["home_team", "away_team"]
            )
    
    # home perspective
    temp_home = df.copy()
    temp_home["team"] = temp_home["home_team"]
    temp_home["opponent"] = temp_home["away_team"]
    temp_home["home"] = 1

    # away perspective
    temp_away = df.copy()
    temp_away["team"] = temp_away["away_team"]
    temp_away["opponent"] = temp_away["home_team"]
    temp_away["home"] = 0

    df["home_goals"] = model.predict(temp_home)
    df["away_goals"] = model.predict(temp_away)

    return df

def convert_to_mins(duration):
    minutes = round(duration / 60,0)
    seconds = round(duration % 60,0)
               
    return minutes, seconds

def calc_remaining(time_start, time_end, n_runs, i):
    time_elapsed = time_end - time_start
    time_average = (time_elapsed) / (i + 1)
    exp_total_time = time_average * n_runs
    exp_time_remaining = exp_total_time - time_elapsed
    pc = round(((i + 1) / (n_runs + 1)) * 100, 1)

    mins, secs = convert_to_mins(exp_time_remaining)
    return [
        mins,
        secs,
        pc
    ]

def print_time_remaining(time_start, time_end, n_runs, i):
    mins, secs, pc = calc_remaining(time_start, time_end, n_runs, i)
    
    if mins == 0:
        print(f'{pc}%: {secs}s remaining')
    else:
        print(f'{pc}%: {mins}mins {secs}s remaining') 