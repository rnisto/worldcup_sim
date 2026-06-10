import pandas as pd
import numpy as np
import knockout

class Team:
    """An object to store information on international teams"""
    def __init__ (self, name, attack, defence):
        self.name = name,
        self.attack = attack,
        self.defence = defence

class Match:
    """An object to store information about games"""
    def __init__(self, home_team, away_team, round = None):
        self.home_team = home_team
        self.away_team = away_team
        self.round = round

        self.home_goals = "NA"
        self.away_goals = "NA"

    def predicted_goals(self, goals_lookup):
        home_avg = goals_lookup[(self.home_team, self.away_team)]["home_goals"]
        away_avg = goals_lookup[(self.home_team, self.away_team)]["away_goals"]

        return home_avg, away_avg

    def simulate_result(self, goals_lookup):
        home_avg, away_avg = self.predicted_goals(goals_lookup)
        self.home_goals = np.random.poisson(home_avg)
        self.away_goals = np.random.poisson(away_avg)
        if self.home_goals > self.away_goals:
            self.outcome = self.home_team
        elif self.home_goals < self.away_goals:
            self.outcome = self.away_team
        else:
            self.outcome = "Draw"

        return self.home_goals, self.away_goals
    
    def simulate_shootout(self):
        self.outcome = np.random.choice([self.home_team, self.away_team])

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
                round = "Group Stage"
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

    def simulate(self, goals_lookup, fixtures):
        self.import_fixtures(fixtures)
        for match in self.matches:
            hg, ag = match.simulate_result(goals_lookup)
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

class KnockoutRound:
    """A class to manage knockout rounds""" 

    def __init__(self, stage, previous_round = None, third_place_qualifiers = None, combination = None):
        self.stage = stage
        self.previous_round = previous_round
        self.third_place_qualifiers = third_place_qualifiers
        self.combination = combination

        self.matches = []

    def add_match(self, home, away):
        self.matches.append(
            Match(
                home_team=home,
                away_team=away
            )
        )

    def build_round(self):
        if self.stage == 32:
            self.matches = knockout.build_first_knockout(self.previous_round, self.combination)
        elif self.stage == 16:
            self.matches = knockout.build_second_knockout(self.previous_round)
        elif self.stage == 8:
            self.matches = knockout.build_quarters(self.previous_round)
        elif self.stage == 4:
            self.matches = knockout.build_semis(self.previous_round)
        elif self.stage == 2:
            self.matches = knockout.build_final(self.previous_round)

    def simulate(self, goals_lookup):
        for match in self.matches:
            match.simulate_result(goals_lookup)
            if match.home_goals == match.away_goals:
                match.simulate_shootout()

        self.save_teams()

    def print_fixtures(self):
        for match in self.matches:
            print(match.home_team + " vs " + match.away_team)

    def print_results(self):
        for match in self.matches:
            if match.home_goals == match.away_goals:
                if match.outcome == match.home_team:
                    print(match.home_team + " p" + str(match.home_goals) +
                  "-" + str(match.away_goals) + " "  + match.away_team)
                elif match.outcome == match.away_team:
                    print(match.home_team + " " + str(match.home_goals) +
                  "-" + str(match.away_goals) + "p "  + match.away_team)
                else: print(match.outcome)
            else:
                print(match.home_team + " " + str(match.home_goals) +
                  "-" + str(match.away_goals) + " "  + match.away_team)
                
    def save_teams(self):
        self.teams = []
        for match in self.matches:
            self.teams.extend([match.home_team, match.away_team])

class WorldCup:
    """A class to manage a whole world cup tournament simulation"""

    def __init__(self, groups):
        self.groups = {g.name: g for g in groups}

        self.teams = []
        for g in self.groups.values():
            self.teams.extend(g.teams)

        self.third_place_table = pd.DataFrame(
            index= [],
            columns=["P","W","D","L","GF","GA","GD","Pts"]
        ).fillna(0)

    def build_third_table(self):
        self.third_place_table = pd.concat(
            [g.table.iloc[[2]] for g in self.groups.values()]
        )

        self.third_place_table = self.third_place_table.sort_values(
            ["Pts", "GD", "GF"],
            ascending=False
        )

        self.third_place_qualifiers = self.third_place_table.index[0:8].tolist()

    def get_group(self, team_name):
        for group in self.groups.values():
            if team_name in group.teams:
                return group.name

        return None

    def get_first_round_combination(self):
        self.combination = ""
        for team in self.third_place_qualifiers:
            self.combination = self.combination + self.get_group(team)

        self.combination = "".join(sorted(self.combination))

    def simulate(self, goals_lookup, fixtures):
        for group in self.groups.values():
            group.simulate(goals_lookup, fixtures)

        self.build_third_table()
        self.get_first_round_combination()

        self.first_round = KnockoutRound(32, self.groups, self.third_place_table, self.combination)
        self.first_round.build_round()      
        self.first_round.simulate(goals_lookup)

        self.second_round = KnockoutRound(16, self.first_round)
        self.second_round.build_round()
        self.second_round.simulate(goals_lookup)  

        self.quarters = KnockoutRound(8, self.second_round)
        self.quarters.build_round()
        self.quarters.simulate(goals_lookup)  

        self.semis = KnockoutRound(4, self.quarters)
        self.semis.build_round()
        self.semis.simulate(goals_lookup)  

        self.final = KnockoutRound(2, self.semis)
        self.final.build_round()
        self.final.simulate(goals_lookup)  

        return self.summarise()

    def get_group_table(self, group_name):
        return self.groups[group_name].table
    
    def all_matches(self):
        return (
            self.first_round.matches
            + self.second_round.matches
            + self.quarters.matches
            + self.semis.matches
            + self.final.matches
        )

    def summarise(self):
        # england_matches = [
        #     m for m in self.all_matches()
        #     if "England" in (m.home_team, m.away_team)
        # ]
        output = pd.DataFrame({
            "team": self.teams,
            "result": "Group",
            "knocked_out_by": None
        })

        rounds = [
            ("R32", self.first_round),
            ("R16", self.second_round),
            ("QF", self.quarters),
            ("SF", self.semis),
            ("Final", self.final),
        ]

        for stage, rnd in rounds:
            for match in rnd.matches:
                winner = match.outcome
                loser = (
                    match.away_team
                    if winner == match.home_team
                    else match.home_team
                )
                output.loc[
                    output["team"] == loser,
                    "knocked_out_by"
                ] = winner

                output.loc[
                    output["team"] == loser,
                    "result"
                ] = stage

        return output