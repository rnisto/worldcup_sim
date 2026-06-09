import pandas as pd

def build_first_knockout(groups, combination):
    import classes
    from combinations import combinations

    combinations = combinations[combinations["third_place"] == combination]
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
    for match in matches:
        match.round = "Round of 32"

    return matches

def build_second_knockout(first_round):
    import classes

    matches = [
        classes.Match(home_team=first_round.matches[0].outcome, 
                      away_team=first_round.matches[2].outcome),
        classes.Match(home_team=first_round.matches[1].outcome, 
                      away_team=first_round.matches[4].outcome),
        classes.Match(home_team=first_round.matches[3].outcome, 
                      away_team=first_round.matches[5].outcome),                     
        classes.Match(home_team=first_round.matches[6].outcome, 
                      away_team=first_round.matches[7].outcome),                     
        classes.Match(home_team=first_round.matches[10].outcome, 
                      away_team=first_round.matches[11].outcome),                      
        classes.Match(home_team=first_round.matches[8].outcome, 
                      away_team=first_round.matches[9].outcome),                     
        classes.Match(home_team=first_round.matches[13].outcome, 
                      away_team=first_round.matches[15].outcome),
        classes.Match(home_team=first_round.matches[12].outcome, 
                      away_team=first_round.matches[14].outcome)                     
    ]

    for match in matches:
        match.round = "Round of 16"
    
    return matches

def build_quarters(second_round):
    import classes

    matches = [
        classes.Match(home_team=second_round.matches[0].outcome, 
                      away_team=second_round.matches[1].outcome),
        classes.Match(home_team=second_round.matches[4].outcome, 
                      away_team=second_round.matches[5].outcome),                   
        classes.Match(home_team=second_round.matches[2].outcome, 
                      away_team=second_round.matches[3].outcome),                      
        classes.Match(home_team=second_round.matches[6].outcome, 
                      away_team=second_round.matches[7].outcome)                     
    ]

    for match in matches:
        match.round = "Quarter Finals"

    return matches

def build_semis(quarters):
    import classes

    matches = [
        classes.Match(home_team=quarters.matches[0].outcome, 
                      away_team=quarters.matches[1].outcome),
        classes.Match(home_team=quarters.matches[2].outcome, 
                      away_team=quarters.matches[3].outcome)                  
                   
    ]

    for match in matches:
        match.round = "Semi Finals"

    return matches

def build_final(semis):
    import classes

    matches = [
        classes.Match(home_team=semis.matches[0].outcome, 
                      away_team=semis.matches[1].outcome,
                      round = "Final")                      
    ]

    return matches