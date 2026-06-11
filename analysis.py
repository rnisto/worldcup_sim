import pandas as pd
import numpy as np
from statsmodels.iolib.smpickle import load_pickle

poisson_model = load_pickle("poisson_model.pkl")

coeffs = poisson_model.params.to_frame(name="coef").reset_index()
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

print(strengths.sort_values(["rating"], ascending=False).head(20))


winners = pd.read_parquet('simulation_winners.parquet')
probabilities = winners["team"].value_counts().reset_index()
probabilities.columns = ["team", "count"]
probabilities["p"] = probabilities["count"] / sum(probabilities["count"])
print(probabilities)


fixtures = pd.read_parquet('simulation_fixtures.parquet')
test = fixtures.melt(id_vars=["team","model_run"], 
                     value_vars=["R32", "R16", "QF", "SF", "Final"],
                     var_name="round",
                     value_name="opponent"
                     )

for round in ["R32", "R16", "QF", "SF", "Final"]:
    opponents = test[
    (test["team"] == "France") &
    (test["round"] == round)
    ]

    result = opponents["opponent"].value_counts(normalize=True).reset_index()
    result.columns = ["opponent", "probability"]

    print(result.head(5))

# knocked_out = outputs.groupby(["team", "result", "knocked_out_by"]).size().reset_index(name="count")
# knocked_out["p"] = knocked_out["count"] / 10000

# print(knocked_out[(knocked_out["team"] == "England") &
#                    (knocked_out["result"] == "R16")].sort_values(["p"], ascending= False))