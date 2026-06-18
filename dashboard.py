import streamlit as st
import pandas as pd
import matplotlib
import colours

results = pd.read_parquet("probabilities.parquet")
results["probability"] = results["probability"].round(2)
results = results.pivot(index = ["team", "outcome"], 
                          columns = "date", 
                          values = "probability"
                          ).reset_index()
results.columns = ["Team", "Outcome", "Pre-tournament","After Round 1"]
results["Change"] = (results["After Round 1"] - results["Pre-tournament"]).round(2)

results["Outcome"] = pd.Categorical(
   results["Outcome"], 
   ["1Q", "2Q", "3Q", "3", "4", "Round of 32", "Round of 16",
    "Quarter Finals", "Semi Finals", "Final", "Winners"
    ])

st.title("2026 Fifa World Cup Projections")
st.text("This apps presents the results of Monte Carlo Simulations of the 2026 World Cup. Teams strengths have been modelled using a simple poisson goals model.")

st.header("The Candidates")
st.text("Probability of winning the tournanment")
winners = results[results["Outcome"] == "Winners"].sort_values(
    "After Round 1", ascending = False
    ).head(10)
winners = winners[["Team", "Pre-tournament", "After Round 1", "Change"]]
winners = (
    winners
    .style
    .format({
        "Pre-tournament": "{:.1%}",
        "After Round 1": "{:.1%}",
        "Change": "{:+.1%}"
    })
    .background_gradient(subset=["Change"], 
                         cmap="RdYlGn")
    .map(colours.style_team, subset=["Team"])
)
st.dataframe(winners, hide_index=True)

st.header("Investigate Team")
team = st.selectbox(
    "Select team",
    sorted(results["Team"].unique())
)

# round_ = st.selectbox(
#     "Select round",
#     sorted(results["outcome"].unique())
# )
st.subheader("Group Stage Outcomes")
group_stage = results[
    (results["Team"] == team) &
    (results["Outcome"].isin(["1Q", "2Q", "3Q", "3", "4"]))
].sort_values("Outcome")

group_stage = (
    group_stage
    .style
    .format({
        "Pre-tournament": "{:.1%}",
        "After Round 1": "{:.1%}",
        "Change": "{:+.1%}"
    })
    .background_gradient(subset=["Change"], 
                         cmap="RdYlGn")
    .map(colours.style_team, subset=["Team"])
)

st.dataframe(group_stage, hide_index=True)

st.subheader("Probability of Reaching Knockout Rounds")
knockouts = results[
    (results["Team"] == team) &
    (~results["Outcome"].isin(["1Q", "2Q", "3Q", "3", "4"]))
].sort_values("Outcome")

knockouts = (
    knockouts
    .style
    .format({
        "Pre-tournament": "{:.1%}",
        "After Round 1": "{:.1%}",
        "Change": "{:+.1%}"
    })
    .background_gradient(subset=["Change"], 
                         cmap="RdYlGn")
    .map(colours.style_team, subset=["Team"])
)

st.dataframe(knockouts, hide_index=True)

st.subheader("Road to the Final")
st.text("These outputs aren't path dependent and so should be treated with some caution, particularly for weaker teams.")
rtf = pd.read_parquet("rtf.parquet")
rtf = rtf[rtf["round"] != "Group Stage"]
rtf["round"] = pd.Categorical(
   rtf["round"], 
   ["Round of 32", "Round of 16",
    "Quarter Finals", "Semi Finals", "Final", "Winners"
    ])
rtf = rtf[["team", "round", "opponent", "probability"]]
rtf.columns = ["Team", "Round", "Opponent", "Probability (given qualified)"]


rtf_filtered = rtf[rtf["Team"] == team]

most_likely = (
    rtf_filtered
    .sort_values(["Round", "Probability (given qualified)"], ascending=[True, False])
    .drop_duplicates("Round")
)

styled = (
    most_likely
    .style
    .format({"Probability (given qualified)": "{:.1%}"})
    .map(colours.style_team, subset=["Team"])
    .map(colours.style_team, subset=["Opponent"])
)

st.dataframe(styled, hide_index=True)

# if not filtered.empty:
#     st.metric(
#         "Probability",
#         f"{filtered.iloc[0]['probability']:.1%}"
#     )