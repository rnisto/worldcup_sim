import pandas as pd
import datetime as datetime
from scipy.stats import poisson

import time
import functions
import gc

from model import build_dataframe
from model import estimate_model

data = pd.read_csv("https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv", on_bad_lines='warn')
data["date"] = pd.to_datetime(data["date"], format='%Y-%m-%d')


results = []

world_cup_dates = [
    (datetime.datetime(2022, 11, 20),datetime.datetime(2022, 12, 18)),
    (datetime.datetime(2018, 6, 14),datetime.datetime(2018, 7, 17)),
    (datetime.datetime(2014, 6, 12),datetime.datetime(2014, 7, 13)),
    (datetime.datetime(2010, 6, 11),datetime.datetime(2010, 7, 11)),
    (datetime.datetime(2006, 6, 9),datetime.datetime(2006, 7, 9)),
    (datetime.datetime(2002, 5, 31),datetime.datetime(2002, 6, 30)),
                   ]
n_runs = 36 * 3
i = 0
time_start = time.perf_counter()
for x in [0.8, 0.9, 1]:
    for rho in [0, -0.001, -0.0015, -0.002, -0.0025]:
        for start, end in world_cup_dates:
            i += 1
            train_input = data[data["date"] < start]
            test_input = data[(data["date"] >= start) & (data["tournament"] == "FIFA World Cup")]

            train = build_dataframe(train_input, rho, start, friendly_weight= x)
            test = build_dataframe(test_input, rho, end, filter = False, friendly_weight= x)
            poisson_model = estimate_model(train)

            pred = poisson_model.predict(test)

            ll = poisson.logpmf(
                test["goals"],
                pred
            ).sum()

            results.append((x, rho, start.year, ll))
            del train, test, poisson_model, pred
            time_end = time.perf_counter()
            functions.print_time_remaining(time_start, time_end, n_runs, i)
    gc.collect()

results_df = pd.DataFrame(results, columns=["friendly_weight", "rho", "world_cup", "log_likelihood"])
results_df = results_df.round(4)

results_df = (
    results_df
    .sort_values(
        ["world_cup", "log_likelihood"],
        ascending=[True, False]
    )
)

for wc, group in results_df.groupby("world_cup"):
    print(f"\n{wc}")
    print(group)

    average_results = (
    results_df
    .groupby(["friendly_weight", "rho"], as_index=False)
    ["log_likelihood"]
    .mean()
    .sort_values("log_likelihood", ascending=False)
)

print(average_results.round(4))