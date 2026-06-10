import pandas as pd
import datetime
import classes
import groups
import functions
import time
from statsmodels.iolib.smpickle import load_pickle

poisson_model = load_pickle("poisson_model.pkl")

raw = pd.read_csv("https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv", on_bad_lines='warn')
raw["date"] = pd.to_datetime(raw["date"], format='%Y-%m-%d')

fixtures = raw[(raw["tournament"] == "FIFA World Cup") &
                (raw["date"] > datetime.datetime(2026, 6, 10))
                ]

teams = functions.get_teams(fixtures)
predicted_goals_lookup = functions.build_predicted_goals_lookup(teams, poisson_model)
predicted_goals_dict = predicted_goals_lookup.set_index(
    ["home_team", "away_team"]
)[["home_goals", "away_goals"]].to_dict("index")

n_runs = 10
fixtures_list = []
winners_list = []
total_time = 0

wc = classes.WorldCup(groups = groups.create_groups(), fixtures = fixtures)
time_start = time.perf_counter()
for i in range(n_runs):
    fixtures, winner = wc.simulate(predicted_goals_dict)
    wc.reset()
    fixtures["model_run"] = i
    winners_list.append(winner)
    fixtures_list.append(fixtures)
    time_end = time.perf_counter()
    if i % 10 == 0: functions.print_time_remaining(time_start, time_end, n_runs, i)
    
fixtures = pd.concat(fixtures_list, ignore_index=True)
winners = pd.DataFrame({
    "team": winners_list,
    "model_run": range(n_runs)
})

print(winners.head(10))
#fixtures.to_parquet("simulation_fixtures.parquet")
#winners.to_parquet("simulation_winners.parquet")