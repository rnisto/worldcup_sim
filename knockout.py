import pandas as pd
import combinations

def build_first_knockout(groups, third_place_table):

    import classes
    matches = [
        classes.Match(home_team=groups["A"].table.index[1], 
                      away_team=groups["B"].table.index[0]),
        classes.Match(home_team=groups["C"].table.index[0], 
                      away_team=groups["F"].table.index[1]),
    ]
    return matches