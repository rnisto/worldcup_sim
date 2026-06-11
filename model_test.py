import pandas as pd
import datetime as datetime
from scipy.stats import poisson

from model import build_dataframe
from model import estimate_model

data = pd.read_csv("https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv", on_bad_lines='warn')
data["date"] = pd.to_datetime(data["date"], format='%Y-%m-%d')

train_input = data[data["date"] < "2018-06-14"]
test_input = data[(data["date"] > "2018-06-14") & (data["tournament"] == "FIFA World Cup")]
results = []

for x in [0.5, 0.7, 0.9, 1]:
    for rho in [0, -0.0015, -0.00175, -0.002, -0.00225 -0.0025]:
        train = build_dataframe(train_input, rho, datetime.datetime(2018, 6, 14), friendly_weight= x)
        test = build_dataframe(test_input, rho, datetime.datetime(2018, 7, 17), filter = False, friendly_weight= x)
        poisson_model = estimate_model(train)

        pred = poisson_model.predict(test)

        ll = poisson.logpmf(
            test["goals"],
            pred
        ).sum()

        results.append((x, rho,ll))

results_df = pd.DataFrame(results, columns=["friendly_weight", "rho", "log_likelihood"])
results_df = results_df.sort_values("log_likelihood", ascending=False)
results_df = results_df.round(4)
print(results_df)