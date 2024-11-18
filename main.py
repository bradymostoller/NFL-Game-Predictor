import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from io import StringIO
standings_url = "https://www.pro-football-reference.com/years/2023/"

data = requests.get(standings_url)

soup = BeautifulSoup(data.text, "lxml")

standings_table = soup.select('table.stats_table')[0]

links = standings_table.find_all('a')

links = [l.get("href") for l in links]
links = [l for l in links if '/teams/' in l]

team_urls = [f"https://www.pro-football-reference.com{l}" for l in links]

columns = [
    "Week", "Day", "Date", "Time", "Boxscore", "Result", "OT", 
    "Record", "Home/Away", "Opponent", "Team Points", "Opponent Points", 
    "First Downs (Team)", "Total Yards (Team)", "Passing Yards (Team)", 
    "Rushing Yards (Team)", "Turnovers (Team)", "First Downs (Opponent)", 
    "Total Yards (Opponent)", "Passing Yards (Opponent)", "Rushing Yards (Opponent)", 
    "Turnovers (Opponent)", "Offense EPA", "Defense EPA", "Special Teams EPA", "Team"
]

all_games = []
for team_url in team_urls:
    team_name = team_url.split("/")[-2]

    data = requests.get(team_url)
    games = pd.read_html(StringIO(data.text), match="Schedule & Game Results Table")[0]
    if isinstance(games.columns, pd.MultiIndex):
        games.columns = games.columns.droplevel()

    # Check if the number of columns matches our custom list, otherwise skip
    if len(games.columns) == len(columns):
        games.columns = columns
    games["Team"] = team_name
    all_games.append(games)
    time.sleep(1)


match_df = pd.concat(all_games)
match_df.columns = [c.lower() for c in match_df.columns]
match_df.to_csv("game_stats.csv", index=False)




    







