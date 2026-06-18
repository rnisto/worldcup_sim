import pandas as pd
import numpy as np
import knockout
import datetime

class Team:
    """An object to store information on international teams"""
    def __init__ (self, name, attack, defence):
        self.name = name,
        self.attack = attack,
        self.defence = defence

class Match:
    """An object to store information about games"""
    def __init__(self, home_team, away_team, location = None, round = None, home_goals = None, away_goals = None):
        self.home_team = home_team
        self.away_team = away_team
        self.location = location
        self.round = round

        self.home_goals = home_goals
        self.away_goals = away_goals

        if self.home_team == self.location:
            self.advantage = "H"
        elif self.away_team == self.location:
            self.advantage = "A"
        else:
            self.advantage = "N"

    def predicted_goals(self, goals_lookup):
        home_avg = goals_lookup[(self.home_team, self.away_team, self.advantage)]["home_goals"]
        away_avg = goals_lookup[(self.home_team, self.away_team, self.advantage)]["away_goals"]

        return home_avg, away_avg

    def simulate_result(self, goals_lookup):
        if ((self.home_goals == None) & (self.away_goals == None)):
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

    def copy(self):
        return Match(
            home_team=self.home_team,
            away_team=self.away_team,
            location=self.location,
            home_goals=self.home_goals,
            away_goals=self.away_goals,
            round = self.round
        )

class Group:
    """A class to store group matches and results"""
    def __init__(self, name, teams):
        self.name = name
        self.teams = teams
        self.team_to_idx = {t: i for i, t in enumerate(self.teams)}

        self.matches = []

        self.pts = np.zeros(len(self.teams))
        self.gf = np.zeros(len(self.teams))
        self.ga = np.zeros(len(self.teams))
        self.w = np.zeros(len(self.teams))
        self.d = np.zeros(len(self.teams))
        self.l = np.zeros(len(self.teams))
        self.table = self.build_table()

    def add_match(self, home, away, location, home_goals, away_goals):
        if pd.isna(home_goals): 
            home_goals = None
            away_goals = None

        self.matches.append(
            Match(
                home_team=home,
                away_team=away,
                location = location,
                home_goals = home_goals,
                away_goals = away_goals,
                round = "Group Stage"
            )
        )

    def import_fixtures(self, fixtures):

        group_fixtures = fixtures[
            (fixtures["home_team"].isin(self.teams)) &
            (fixtures["away_team"].isin(self.teams)) &
            (fixtures["date"] < datetime.datetime(2026,6,28))
        ]

        for _, row in group_fixtures.iterrows():
            self.add_match(
                home=row["home_team"],
                away=row["away_team"],
                location=row["country"],
                home_goals = row["home_score"],
                away_goals = row["away_score"]
            )

        self.save_fixtures()

    def save_fixtures(self):
        self.fixtures = [m.copy() for m in self.matches]

    def update_table(self, home, away, hg, ag):
        h = self.team_to_idx[home]
        a = self.team_to_idx[away]

        self.gf[h] += hg
        self.ga[h] += ag
        self.gf[a] += ag
        self.ga[a] += hg

        self.pts[h] += 1
        self.pts[a] += 1

        if hg > ag:
            self.w[h] += 1
            self.l[a] += 1
            self.pts[h] += 2
        elif ag > hg:
            self.w[a] += 1
            self.l[h] += 1
            self.pts[a] += 2
        else:
            self.d[h] += 1
            self.d[a] += 1
            self.pts[h] += 1
            self.pts[a] += 1

    def build_table(self):
        df = pd.DataFrame({
            "team": self.teams,
            "Pts": self.pts,
            "GF": self.gf,
            "GA": self.ga,
        })

        df["GD"] = df["GF"] - df["GA"]

        df = df.sort_values(
            ["Pts", "GD", "GF"],
            ascending=False
        )
        df = df.set_index("team")
        return df

    def simulate(self, goals_lookup):
        for match in self.matches:
            hg, ag = match.simulate_result(goals_lookup)
            self.update_table(
                match.home_team,
                match.away_team,
                hg,
                ag
            )

        self.table = self.build_table()
        return self.table
    
    def print_results(self):
        for match in self.matches:
            print(match.home_team + " " + str(match.home_goals) +
                  "-" + str(match.away_goals) + " "  + match.away_team)
            
    def reset(self):
        self.matches = [m.copy() for m in self.fixtures]

        self.pts = np.zeros(len(self.teams))
        self.gf = np.zeros(len(self.teams))
        self.ga = np.zeros(len(self.teams))
        self.w = np.zeros(len(self.teams))
        self.d = np.zeros(len(self.teams))
        self.l = np.zeros(len(self.teams))
        self.table = self.build_table()

class KnockoutRound:
    """A class to manage knockout rounds""" 

    def __init__(self, stage):
        self.stage = stage
        self.previous_round = None
        self.combination = None
        self.r32_combinations = None

        self.matches = []
        self.teams = []

    def add_match(self, home, away):
        self.matches.append(
            Match(
                home_team=home,
                away_team=away
            )
        )

    def build_round(self, previous_round = None, combination = None, r32_combinations = None):
        if self.stage == 32:
            self.matches = knockout.build_first_knockout(previous_round, combination, r32_combinations)
        elif self.stage == 16:
            self.matches = knockout.build_second_knockout(previous_round)
        elif self.stage == 8:
            self.matches = knockout.build_quarters(previous_round)
        elif self.stage == 4:
            self.matches = knockout.build_semis(previous_round)
        elif self.stage == 2:
            self.matches = knockout.build_final(previous_round)

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
        for match in self.matches:
            self.teams.extend([match.home_team, match.away_team])

    def reset(self):
        self.matches = []
        self.teams = []

class WorldCup:
    """A class to manage a whole world cup tournament simulation"""

    def __init__(self, groups, fixtures):
        self.groups = {g.name: g for g in groups}
        self.teams = []
        self.fixtures = fixtures

        from combinations import combinations
        self.r32_combinations = combinations

        self.build_tournament()

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
       
    def build_tournament(self):
        for g in self.groups.values():
            self.teams.extend(g.teams)
            g.import_fixtures(self.fixtures)

        self.third_place_table = pd.DataFrame(
            index= [],
            columns=["P","W","D","L","GF","GA","GD","Pts"]
        ).fillna(0)

        self.first_round = KnockoutRound(32)
        self.second_round = KnockoutRound(16)
        self.quarters = KnockoutRound(8)
        self.semis = KnockoutRound(4)
        self.final = KnockoutRound(2)

    def simulate(self, goals_lookup):
        for group in self.groups.values():
            group.simulate(goals_lookup)

        self.build_third_table()
        self.get_first_round_combination()

        self.first_round.build_round(previous_round = self.groups,
                                     combination = self.combination,
                                     r32_combinations = self.r32_combinations
                                     )      
        self.first_round.simulate(goals_lookup)

        self.second_round.build_round(self.first_round)
        self.second_round.simulate(goals_lookup)  

        self.quarters.build_round(self.second_round)
        self.quarters.simulate(goals_lookup)  

        self.semis.build_round(self.quarters)
        self.semis.simulate(goals_lookup)  

        self.final.build_round(self.semis)
        self.final.simulate(goals_lookup)  

        return self.summarise()

    def get_group_table(self, group_name):
        return self.groups[group_name].table
    
    def all_matches(self):
        matches = []

        for group in self.groups.values():
            matches.extend(group.matches)

        matches.extend(self.first_round.matches)
        matches.extend(self.second_round.matches)
        matches.extend(self.quarters.matches)
        matches.extend(self.semis.matches)
        matches.extend(self.final.matches)

        return matches
    
    def summarise(self):
        rows = []

        for match in self.all_matches():
            rows.append({
                "home_team": match.home_team,
                "away_team": match.away_team,
                "home_goals": match.home_goals,
                "away_goals": match.away_goals,
                "round": match.round,
                "winner": match.outcome,
                "advantage": match.advantage
            })

        results = pd.DataFrame(rows)
        return results
        # rounds = [
        #     ("R32", self.first_round),
        #     ("R16", self.second_round),
        #     ("QF", self.quarters),
        #     ("SF", self.semis),
        #     ("Final", self.final),
        # ]

        # for stage, rnd in rounds:
        #     for match in rnd.matches:
        #         fixtures.loc[
        #             fixtures["team"] == match.home_team,
        #             stage                           
        #         ] = match.away_team
        
        #         fixtures.loc[
        #             fixtures["team"] == match.away_team,
        #             stage                           
        #         ] = match.home_team

        #         winner = self.final.matches[0].outcome
        # return [fixtures, winner]

    def reset(self):
        for group in self.groups.values():
            group.reset()
        self.first_round.reset()
        self.second_round.reset()
        self.quarters.reset()
        self.semis.reset()
        self.final.reset()

        self.third_place_table = pd.DataFrame(
            index= [],
            columns=["P","W","D","L","GF","GA","GD","Pts"]
        ).fillna(0)