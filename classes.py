import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
from scipy.stats import poisson
import numpy as np

class Team:
    """An object to store information on international teams"""
    def __init__ (self, name, attack, defence):
        self.name = name,
        self.attack = attack,
        self.defence = defence

class Match:
    """An object to store information about games"""
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team

        self.home_goals = "NA"
        self.away_goals = "NA"

    def predicted_goals(self, model):
        home_avg = model.predict(
            pd.DataFrame({
                "team": [self.home_team],
                "opponent": [self.away_team],
                "home": [0]
            })
        ).iloc[0]

        away_avg = model.predict(
            pd.DataFrame({
                "team": [self.away_team],
                "opponent": [self.home_team],
                "home": [0]
            })
        ).iloc[0]

        return home_avg, away_avg

    def simulate_result(self, model):
        home_avg, away_avg = self.predicted_goals(model)

        self.home_goals = np.random.poisson(home_avg)
        self.away_goals = np.random.poisson(away_avg)

        return self.home_goals, self.away_goals
    
    def simulate_shootout(self):
        winner = np.random.choice([self.home_team, self.away_team])

        return winner

class Group:
    """A class to store group matches and results"""
    def __init__(self, name, teams):
        self.name = name
        self.teams = teams

        self.matches = []

        self.table = pd.DataFrame(
            index=teams,
            columns=["P","W","D","L","GF","GA","GD","Pts"]
        ).fillna(0)

    def add_match(self, home, away):
        self.matches.append(
            Match(
                home_team=home,
                away_team=away,
            )
        )

    def import_fixtures(self, fixtures):
        for team in self.teams:
            group_fixtures = fixtures[
                fixtures["home_team"].isin(self.teams) &
                fixtures["away_team"].isin(self.teams)
            ]

        for _, row in group_fixtures.iterrows():
            self.add_match(
                home=row["home_team"],
                away=row["away_team"]
            )

    def update_table(self, home, away, hg, ag):
        self.table.loc[home, "P"] += 1
        self.table.loc[away, "P"] += 1

        self.table.loc[home, "GF"] += hg
        self.table.loc[home, "GA"] += ag

        self.table.loc[away, "GF"] += ag
        self.table.loc[away, "GA"] += hg

        if hg > ag:
            self.table.loc[home, "W"] += 1
            self.table.loc[away, "L"] += 1

            self.table.loc[home, "Pts"] += 3

        elif ag > hg:
            self.table.loc[away, "W"] += 1
            self.table.loc[home, "L"] += 1

            self.table.loc[away, "Pts"] += 3

        else:
            self.table.loc[home, "D"] += 1
            self.table.loc[away, "D"] += 1

            self.table.loc[home, "Pts"] += 1
            self.table.loc[away, "Pts"] += 1

    def simulate(self, model):
        for match in self.matches:
            hg, ag = match.simulate_result(model)
            self.update_table(
                match.home_team,
                match.away_team,
                hg,
                ag
            )

        self.table["GD"] = (
            self.table["GF"] - self.table["GA"]
        )
        
        self.table = self.table.sort_values(
            ["Pts", "GD", "GF"],
            ascending=False
        )

        return self.table
    
    def print_results(self):
        for match in self.matches:
            print(match.home_team + " " + str(match.home_goals) +
                  "-" + str(match.away_goals) + " "  + match.away_team)