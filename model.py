import pandas as pd
import numpy as np
import datetime as datetime
import statsmodels.api as sm
import statsmodels.formula.api as smf

raw = pd.read_csv("https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv", on_bad_lines='warn')
data = raw
data["date"] = pd.to_datetime(raw["date"], format='%Y-%m-%d')

data["days_since"] = (datetime.datetime.today() - data["date"]).dt.days
data["time_weight"] = np.exp(data["days_since"] * -0.0018)
lookback_period = datetime.timedelta(days = 365 * 5)
data = data[(data["days_since"] < 365*5) & (data["days_since"] > 0)]
data["comp_weight"] = np.where(
    data["tournament"] == "Friendly",
    0.5,
    1.0
)
data["weight"] = data["comp_weight"] * data["time_weight"]

# filtering teams with limited games
data = data.groupby('home_team').filter(lambda x: len(x) >= 10)
data = data.groupby('away_team').filter(lambda x: len(x) >= 10)

goal_model_data = data[["home_team", "away_team", "home_score", 
                        "neutral", "weight"]]
goal_model_data["home"] = np.where(goal_model_data["neutral"] == True, 0, 1)
goal_model_data = goal_model_data[[
    "home_team", "away_team", "home_score", "home", "weight"
    ]]
goal_model_data = goal_model_data.rename(columns={"home_team":"team", "away_team":"opponent", "home_score":"goals", "home":"home"})
goal_model_data = pd.concat([goal_model_data, data[["away_team", "home_team", "away_score"]].assign(home=0).rename(
    columns={"away_team":"team", "home_team":"opponent", "away_score":"goals"}
)])

poisson_model = smf.glm(formula="goals ~ home + team + opponent", 
                        data=goal_model_data,  
                        family=sm.families.Poisson(),
                        freq_weights=data.loc[goal_model_data.index, "weight"]
                        ).fit()

poisson_model.save("poisson_model.pkl")

coeffs = poisson_model.params.to_frame(name="coef").reset_index()
coeffs.columns = ["team", "value"]
coeffs = coeffs[~coeffs["team"].isin(["Intercept", "home"])]

attack = coeffs[coeffs["team"].str.contains("team")]
defence = coeffs[coeffs["team"].str.contains("opponent")]