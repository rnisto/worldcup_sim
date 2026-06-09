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
    def __init__(self, date, competition, home_team, away_team):
        self.date = date
        self.competition = competition
        self.home_team = home_team
        self.away_team = away_team

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

        home_goals = np.random.poisson(home_avg)
        away_goals = np.random.poisson(away_avg)

        return home_goals, away_goals
    
    def simulate_shootout(self):
        winner = np.random.choice([self.home_team, self.away_team])

        return winner

