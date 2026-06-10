import pandas as pd
from itertools import permutations

def get_teams(fixtures):
    return pd.concat(
        [fixtures["home_team"], fixtures["away_team"]]
    ).drop_duplicates().tolist()



def build_predicted_goals_lookup(teams, model): 
    predicted_goals_lookup = pd.DataFrame( 
        permutations(teams, 2), 
        columns=["home_team", "away_team"] 
        )
    temp_h = predicted_goals_lookup.rename(columns={
        "home_team":"team", "away_team":"opponent", "home_goals":"goals"
        }) 
    temp_a = predicted_goals_lookup.rename(columns={
            "away_team":"team", "home_team":"opponent", "away_goals":"goals"
        })    
    temp_h["home"] = 0
    temp_a["home"] = 0

    predicted_goals_lookup["home_goals"] = model.predict(temp_h)
    predicted_goals_lookup["away_goals"] = model.predict(temp_a)
    return(predicted_goals_lookup)