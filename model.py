import pandas as pd
import numpy as np
import datetime as datetime
import statsmodels.api as sm
import statsmodels.formula.api as smf

def build_dataframe(data, rho, end_date, filter = True, friendly_weight = 0.5):
    data["days_since"] = (end_date - data["date"]).dt.days
    data["time_weight"] = np.exp(data["days_since"] * rho)
    data = data[(data["days_since"] < 365*5) & (data["days_since"] > 0)]
    data["comp_weight"] = np.where(
        data["tournament"] == "Friendly",
        friendly_weight,
        1.0
    )
    data["weight"] = data["comp_weight"] * data["time_weight"]

    # filtering teams with limited games
    if filter == True:
        data = data.groupby('home_team').filter(lambda x: len(x) >= 10)
        data = data.groupby('away_team').filter(lambda x: len(x) >= 10)

    goal_model_data = data[["home_team", "away_team", "home_score", 
                            "neutral", "weight"]]
    goal_model_data["home"] = np.where(goal_model_data["neutral"] == True, 0, 1)
    goal_model_data = goal_model_data[[
        "home_team", "away_team", "home_score", "home", "weight"
        ]]
    goal_model_data = goal_model_data.rename(columns={"home_team":"team", "away_team":"opponent", "home_score":"goals", "home":"home"})
    goal_model_data = pd.concat([goal_model_data, data[["away_team", "home_team", "away_score", "weight"]].assign(home=0).rename(
        columns={"away_team":"team", "home_team":"opponent", "away_score":"goals"}
    )])

    return goal_model_data

def estimate_model(data):
    poisson_model = smf.glm(formula="goals ~ home + team + opponent", 
                            data=data,  
                            family=sm.families.Poisson(),
                            freq_weights=data["weight"].to_numpy()
                            ).fit()
    return poisson_model

data = pd.read_csv("https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv", on_bad_lines='warn')
data["date"] = pd.to_datetime(data["date"], format='%Y-%m-%d')

model_data = build_dataframe(data, rho = -0.0015, 
                             end_date = datetime.datetime(2026, 6, 10),
                             friendly_weight=1
                             )
poisson_model = estimate_model(model_data)

poisson_model.save("poisson_model.pkl")

