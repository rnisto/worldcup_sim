import pandas as pd
import numpy as np

data = pd.read_csv("https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv", on_bad_lines='warn')
data["date"] = pd.to_datetime(data["date"], format='%Y-%m-%d')

print(data.sample(10))