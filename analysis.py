import pandas as pd

outputs = pd.read_parquet('world_cup_simulations.parquet')

probabilities = outputs.groupby(["team", "result"]).size().reset_index(name="count")
probabilities["p"] = probabilities["count"] / 10000

print(probabilities[probabilities["team"] == "England"])
print(probabilities[probabilities["result"] == "Winner"].sort_values(["p"], ascending=False))

knocked_out = outputs.groupby(["team", "result", "knocked_out_by"]).size().reset_index(name="count")
knocked_out["p"] = knocked_out["count"] / 10000

print(knocked_out[(knocked_out["team"] == "England") &
                   (knocked_out["result"] == "R16")].sort_values(["p"], ascending= False))