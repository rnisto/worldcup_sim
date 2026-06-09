import pandas as pd
import numpy as np
import datetime as datetime

data = pd.read_csv("https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv", on_bad_lines='warn')
data["date"] = pd.to_datetime(data["date"], format='%Y-%m-%d')

data["days_since"] = (datetime.datetime.today() - data["date"]).dt.days
data["time_weight"] = np.exp(data["days_since"] * -0.0018)

lookback_period = datetime.timedelta(days = 365 * 5)

data = data[(data["days_since"] < 365*5) & (data["days_since"] > 0)]

print(data.sample(10))