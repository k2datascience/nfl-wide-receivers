import requests
from bs4 import BeautifulSoup
import pickle
import pandas as pd
import numpy as np
import sqlite3

def scrape_stats(start_year=2010, end_year=2016):
    "Function to scrape wide receiver statistics by year range"
    stats_store = []
    start = int(start_year)
    end = int(end_year)

    for i in range(start, end+1):
        print("Scraping data for season {0}".format(i))
        url = "https://www.pro-football-reference.com/years/" + str(i) + "/receiving.htm"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        stats_table = soup.find(id="all_receiving")
        players = stats_table.find_all("tr")

        for player in players:
            player = player.find_all("td")

            row = {}

            try:
                row['name'] = player[0].get_text()
                row['demo_link'] = player[0].find('a')['href']
                row['team'] = player[1].get_text()
                row['age'] = player[2].get_text()
                row['position'] = player[3].get_text()
                row['games'] = player[4].get_text()
                row['games_start'] = player[5].get_text()
                row['targets'] = player[6].get_text()
                row['receptions'] = player[7].get_text()
                row['catch_pct'] = player[8].get_text()
                row['rec_yards'] = player[9].get_text()
                row['yards_per_rec'] = player[10].get_text()
                row['td'] = player[11].get_text()
                row['longest_rec'] = player[12].get_text()
                row['rec_per_game'] = player[13].get_text()
                row['rec_yards_per_game'] = player[14].get_text()
                row['fumble'] = player[15].get_text()

                stats_store.append(row)

            except:
                # print("Ran into header row.")
                pass

    pickle.dump(stats_store, open("../data/raw/stats_store.p", "wb"))
    return stats_store


def scrape_players(stats_store):
    "Function to scrape player demographic data"
    for i, player in enumerate(stats_store):

        if i % 100 == 0:
            print("Scraping {0} demographics. He is number {1} out of {2}".format(player['name'], i, len(stats_store)))

        url = "https://www.pro-football-reference.com/" + str(player['demo_link'])
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        try:
            stats_store[i]['height'] = soup.find(itemprop="height").get_text()
            stats_store[i]['weight'] = soup.find(itemprop="weight").get_text()

        except:
            # print("No demographic info")
            pass


    stats_player_store = stats_store
    pickle.dump(stats_player_store, open("../data/raw/stats_player_store.p", "wb"))
    return stats_player_store


def convert_numeric(row, col):
    "Function to convert string to float"
    try:
        val = float(row[col])
        return val
    except:
        print(row[col])
        return np.nan

def lowercase(row, col):
    "Function to convert string to all lowercase"
    try:
        val = row[col].lower()
        return val
    except:
        print(row[col])
        return np.nan

def clean_string(row, col, char):
    "Function to remove extra characters"
    try:
        val = row[col].strip(char)
        return val
    except:
        print(row[col])
        return np.nan

def convert_height(row, col):
    "Function to convert height to inches"
    try:
        val = row[col].split("-")
        val = int(val[0]) * 12 + int(val[1])
        return val
    except:
        print(row[col])
        return np.nan

lower = ["team", "position"]
string_clean = {"catch_pct": "%", "weight": "lb", "name": "*+"}
floats = ["age", "fumble", "games", "games_start", "longest_rec", "rec_per_game", "rec_yards", "rec_yards_per_game", "receptions", "targets", "td", "yards_per_rec", "catch_pct", "weight", "height"]

def clean_data_store_sql(data):
    "Function to clean data formatting and export to SQLite database"
    df = pd.DataFrame(data)

    df["height"] = df.apply(lambda x: convert_height(x, "height"), 1)

    for k, v in string_clean.items():
        df[k] = df.apply(lambda x: clean_string(x, k, v), 1)

    for col in floats:
        df[col] = df.apply(lambda x: convert_numeric(x, col), 1)

    for col in lower:
        df[col] = df.apply(lambda x: lowercase(x, col), 1)

    # create a new feature for targets per game
    df['targets_per_game'] = df['targets'] / df['games']

    conn = sqlite3.connect("../data/processed/nfl_wr.db")
    df.to_sql("wide_receivers", conn, if_exists="replace")
    conn.close()

    return df
