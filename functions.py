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