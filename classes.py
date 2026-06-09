class Team:
    """An object to store information on international teams"""
    def __init__ (self, name, attack, defence):
        self.name = name,
        self.attack = attack,
        self.defence = defence

class Match:
    """An object to store information about games"""
    def __init__(self, date, competition, home_team, away_team, 
                 home_goals, away_goals, neutral, result):
        self.date = date
        self.competition = competition
        self.home_team = home_team
        self.away_team = away_team
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.neutral = neutral
        self.result = result
