import pandas as pd
import datetime
import classes
import groups
import functions
import time
from statsmodels.iolib.smpickle import load_pickle
import gc
import datetime as datetime

model_name = f'{datetime.date.today().strftime('%y%m%d')}_model.pkl'
poisson_model = load_pickle(model_name)

raw = pd.read_csv("https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv", on_bad_lines='warn')
raw["date"] = pd.to_datetime(raw["date"], format='%Y-%m-%d')

fixtures = raw[(raw["tournament"] == "FIFA World Cup") &
                (raw["date"] > datetime.datetime(2026, 6, 10))
                ]

teams = functions.get_teams(fixtures)
predicted_goals_lookup = functions.build_predicted_goals_lookup(teams, poisson_model)
predicted_goals_dict = predicted_goals_lookup.set_index(
    ["home_team", "away_team", "advantage"]
)[["home_goals", "away_goals"]].to_dict("index")

n_runs = 100000
all_results = []
total_time = 0

wc = classes.WorldCup(groups = groups.create_groups(), fixtures = fixtures)
time_start = time.perf_counter()
for i in range(n_runs):
    output = wc.simulate(predicted_goals_dict)
    wc.reset()
    output["model_run"] = i
    all_results.append(output)
    time_end = time.perf_counter()
    if i % 10 == 0: functions.print_time_remaining(time_start, time_end, n_runs, i)
    if i % 100 == 0: gc.collect()
    
results = pd.concat(all_results, ignore_index=True)

sim_name = f'{datetime.date.today().strftime('%y%m%d')}_simulations.parquet'
results.to_parquet(sim_name)