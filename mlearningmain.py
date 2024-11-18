import pandas as pd  
import numpy as np
from sklearn.ensemble import RandomForestClassifier
games = pd.read_csv("game_stats2.csv", index_col = 0)

def update_year(date_str):
    if pd.isna(date_str):
        return date_str
    if "January" in date_str or "February" in date_str:
        return date_str + ", 2024"
    else:
        return date_str + ", 2023"

# Apply the function to each date in the DataFrame
games["date"] = games["date"].apply(update_year)

# Convert the updated date to datetime
games["date"] = pd.to_datetime(games["date"], format="%B %d, %Y", errors="coerce")

# Format it as DD-MM-YYYY
games["formatted_date"] = games["date"].dt.strftime("%d-%m-%Y")



games["venue_code"] = np.where(games["home/away"] == "@", 0, 1)
games["opp_code"] = games["opp"].astype("category").cat.codes

day_mapping = {
    "Mon": 0,
    "Tue": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6
}
games["day_code"] = games["day"].map(day_mapping)

games["target"] = (games["result"] == "W").astype("int")
rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)
train = games[games["date"] < '2023-10-23'] 
test = games[games["date"] > '2023-10-23']

predictors = ["venue_code", "opp_code", "day_code"]
rf.fit(train[predictors], train["target"])
preds = rf.predict(test[predictors])
from sklearn.metrics import accuracy_score
acc = accuracy_score(test["target"], preds)

combined = pd.DataFrame(dict(actual=test["target"], prediction = preds))


from sklearn.metrics import precision_score
precision = precision_score(test["target"], preds)
print(precision)

grouped_games = games.groupby("team")
group = grouped_games.get_group("pit")

def rolling_averages(group, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed='left').mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset = new_cols)
    return group



cols = ["tmpoints","opppoints", "totyd", "opptotyd"]
new_cols = [f"{c}_rolling" for c in cols]


games_rolling = (games.groupby("team")
                    .apply(lambda x: rolling_averages(x, cols, new_cols))
                    .reset_index(drop=True))
games_rolling.index = range(games_rolling.shape[0])
print(games_rolling)








