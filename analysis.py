import pandas as pd
import numpy as np
from statsmodels.iolib.smpickle import load_pickle
import groups
import datetime

def get_team_strengths(model):
    # calculating team strengths
    coeffs = model.params.to_frame(name="coef").reset_index()
    coeffs.columns = ["team", "value"]
    coeffs = coeffs[~coeffs["team"].isin(["Intercept", "home"])]

    attack = coeffs[coeffs["team"].str.contains("team")].copy()
    attack["team"] = attack["team"].str.extract(r"\[T\.(.*?)\]")
    attack = attack.rename(columns={"value": "attack"})

    defence = coeffs[coeffs["team"].str.contains("opponent")].copy()
    defence["team"] = defence["team"].str.extract(r"\[T\.(.*?)\]")
    defence = defence.rename(columns={"value": "defence"})

    strengths = attack[["team", "attack"]].merge(
        defence[["team", "defence"]],
        on="team",
        how="outer"
    )

    strengths["rating"] = np.exp(strengths["attack"]) * np.exp(-strengths["defence"])
    strengths["rating"] = (strengths["rating"] / strengths["rating"].max()) * 100

    return strengths.sort_values(["rating"], ascending=False)

def get_fifa_rankings(file):

    TEAM_NAME_MAP = {
    # fifa:main
    "Cabo Verde": "Cape Verde",
    "China PR": "China",
    "Czechia": "Czech Republic",
    "Côte d'Ivoire": "Ivory Coast",
    "IR Iran": "Iran",
    "Korea Republic": "South Korea",
    "Türkiye": "Turkey",
    "USA": "United States",
    "US Virgin Islands": "United States Virgin Islands",
    "Kyrgyz Republic": "Kyrgyzstan",
    "DPR Korea": "North Korea",
    "Congo DR": "DR Congo",
    "St. Kitts and Nevis": "Saint Kitts and Nevis",
    "St. Lucia": "Saint Lucia",
    "St. Vincent / Grenadines": "Saint Vincent and the Grenadines",
    "The Gambia": "Gambia"
    }
    
    fifa_rankings = pd.read_csv(file, 
                                encoding= 'unicode_escape',
                                header = None
                                )
    fifa_rankings = fifa_rankings[[1,4]]
    fifa_rankings.columns = ["team", "elo"]
    fifa_rankings["elo"] = fifa_rankings["elo"].str.replace("*","")
    fifa_rankings["elo"] = pd.to_numeric(fifa_rankings["elo"])
    fifa_rankings["team"] = fifa_rankings["team"].replace(TEAM_NAME_MAP)
    return fifa_rankings

def get_win_prob(data):
    data = data[data["round"] == "Final"].value_counts(data["winner"]).reset_index()
    data.columns = ["team", "count"]
    data["p"] = data["count"] / sum(data["count"])
    data["round"] = "Winners"
    return data

def get_round_prob(data, round):
    n_runs = data["model_run"].nunique()
    data = data[data["round"] == round]
    data = data.melt(id_vars=["round","model_run"], 
                     value_vars=["home_team","away_team"],
                     var_name="home / away",
                     value_name="team"
                     )
    counts = (
            data["team"]
            .value_counts()
            .reset_index()
        )

    counts.columns = ["team", "count"]

    counts["p"] = counts["count"] / n_runs
    counts["round"] = round
    return counts

def get_group_standings(data):
    group_map = {}
    for g in groups.create_groups():
        for t in g.teams:
            group_map[t] = g.name  # or group letter

    data = data[data["round"] == "Group Stage"].copy()
    

    home = data[["model_run", "home_team", "home_goals", "away_goals"]].copy()
    home.columns = ["model_run", "team", "gf", "ga"]
    home["pts"] = np.where(home["gf"] > home["ga"], 3,
                    np.where(home["gf"] == home["ga"], 1, 0))
    
    away = data[["model_run", "away_team", "away_goals", "home_goals"]].copy()
    away.columns = ["model_run", "team", "gf", "ga"]
    away["pts"] = np.where(away["gf"] > away["ga"], 3,
                    np.where(away["gf"] == home["ga"], 1, 0))
    
    away["ga"] = home["gf"].values

    all_matches = pd.concat([home, away])

    standings = all_matches.groupby(["model_run", "team"]).agg(
        pts=("pts", "sum"),
        gf=("gf", "sum"),
        ga=("ga", "sum")
    ).reset_index()

    standings["gd"] = standings["gf"] - standings["ga"]
    standings["group"] = standings["team"].map(group_map)

    standings = standings.sort_values(
        ["model_run", "group", "pts", "gd", "gf"],
        ascending=[True, True, False, False, False]
    )

    standings["position"] = standings.groupby(
        ["model_run", "group"]
    ).cumcount() + 1

    return standings

def get_group_prob(standings):
    probabilities = (
        standings.groupby(["team", "position"])
        .size()
        .reset_index(name="count")
    )

    probabilities["p"] = probabilities["count"] / probabilities.groupby("team")["count"].transform("sum")
    probabilities.columns = ["team", "round", "count", "p"]
    probabilities["round"] = np.where(
        probabilities["round"] < 3,
        probabilities["round"].astype(str) + "Q",
        probabilities["round"].astype(str)
    )
    return probabilities

def get_thirdq_prob(df):
    p_stage = df.copy()
    p_stage = p_stage.pivot(index="team", columns="round", values="p").reset_index()
    p_stage["3Q"] = (
    p_stage["Round of 32"]
    - p_stage["1Q"]
    - p_stage["2Q"]
    )
    p_stage["3"] = (
        p_stage["3"] - p_stage["3Q"]
    )
    out = p_stage.melt(id_vars = "team",
                       value_vars = ["Round of 32", "Round of 16",
                                     "Quarter Finals", "Semi Finals",
                                     "Final", "Winners", "1Q", "2Q", "3Q",
                                     "3", "4"
                                     ],
                                     var_name = "outcome",
                                     value_name = "probability"
                       )

    return out

def check_probabilities(df):
    test = df.copy()
    test = test.pivot(index="team", columns="outcome", values="probability").reset_index()
    test["Quali_test"] = test["Round of 32"] - test["1Q"] - test["2Q"] - test["3Q"]
    test["Group_sum_test"] = 1 - (test["1Q"] + test["2Q"] + test["3Q"] + test["3"] + test["4"])
    test["Sequencing1"] = test["Final"] < test["Semi Finals"]
    test["Sequencing2"] = test["Semi Finals"] < test["Quarter Finals"]
    test["Sequencing3"] = test["Quarter Finals"] < test["Round of 16"]
    test["Sequencing4"] = test["Round of 16"] < test["Round of 32"]
    print(test[["Quali_test", "Group_sum_test", "Sequencing1", 
                "Sequencing2", "Sequencing3", "Sequencing4"]].sample(20))

def get_probabilities(df):
    rounds = ["Round of 32", "Round of 16", "Quarter Finals",
            "Semi Finals", "Final"]

    prob_list = []
    for round in rounds:
        prob = get_round_prob(df,round)
        prob_list.append(prob)

    prob_list.append(get_win_prob(df))
    standings = get_group_standings(df)
    prob_list.append(get_group_prob(standings))
    df = pd.concat(prob_list, ignore_index=True)
    out = get_thirdq_prob(df)

    #check_probabilities(out)

    return out

dates = [datetime.datetime(2026,6,10), datetime.datetime(2026,6,18)]

strengths_list = []
probabilities_list = []

for d in dates:
    model_name = f'{d.strftime('%y%m%d')}_model.pkl'
    poisson_model = load_pickle(model_name)
    strengths = get_team_strengths(poisson_model)
    rankings = get_fifa_rankings("./june11_fifa_rankings.csv")

    output = strengths.merge(rankings, on="team", how="inner")
    output["date"] = d
    strengths_list.append(output)
    
    print("Pearson :", output["rating"].corr(output["elo"], method="pearson"))
    print("Spearman:", output["rating"].corr(output["elo"], method="spearman"))

    sim_name = f'{d.strftime('%y%m%d')}_simulations.parquet'
    simulation_results = pd.read_parquet(sim_name)
    probabilities = get_probabilities(simulation_results)
    probabilities["date"] = d
    probabilities_list.append(probabilities)

strengths = pd.concat(strengths_list)
strengths.to_parquet("strengths.parquet")

probabilities = pd.concat(probabilities_list)
probabilities.to_parquet("probabilities.parquet")