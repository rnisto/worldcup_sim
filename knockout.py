import pandas as pd

def build_first_knockout(groups, third_place_qualifiers, combination):
    import classes
    from combinations import combinations

    combinations = combinations[combinations["third_place"] == combination]
    print(combination)
    matches = [
        classes.Match(home_team=groups["A"].table.index[1], 
                      away_team=groups["B"].table.index[0]),
        classes.Match(home_team=groups["C"].table.index[0], 
                      away_team=groups["F"].table.index[1]),
        classes.Match(home_team=groups["E"].table.index[0], 
                      away_team=groups[combinations["1E"].values[0]].table.index[2]),
        classes.Match(home_team=groups["F"].table.index[0], 
                      away_team=groups["C"].table.index[1]),              
        classes.Match(home_team=groups["E"].table.index[1], 
                      away_team=groups["I"].table.index[1]),                     
        classes.Match(home_team=groups["I"].table.index[0], 
                      away_team=groups[combinations["1I"].values[0]].table.index[2]),
        classes.Match(home_team=groups["A"].table.index[0], 
                      away_team=groups[combinations["1A"].values[0]].table.index[2]),
        classes.Match(home_team=groups["L"].table.index[0], 
                      away_team=groups[combinations["1L"].values[0]].table.index[2]),
        classes.Match(home_team=groups["G"].table.index[0], 
                      away_team=groups[combinations["1G"].values[0]].table.index[2]),
        classes.Match(home_team=groups["D"].table.index[0], 
                      away_team=groups[combinations["1D"].values[0]].table.index[2]),
        classes.Match(home_team=groups["H"].table.index[0], 
                      away_team=groups["J"].table.index[1]),              
        classes.Match(home_team=groups["K"].table.index[1], 
                      away_team=groups["L"].table.index[1]),  
        classes.Match(home_team=groups["B"].table.index[0], 
                      away_team=groups[combinations["1B"].values[0]].table.index[2]),
        classes.Match(home_team=groups["D"].table.index[1], 
                      away_team=groups["G"].table.index[1]), 
        classes.Match(home_team=groups["J"].table.index[0], 
                      away_team=groups["H"].table.index[1]),                       
        classes.Match(home_team=groups["K"].table.index[0], 
                      away_team=groups[combinations["1K"].values[0]].table.index[2]),
    ]
    return matches
