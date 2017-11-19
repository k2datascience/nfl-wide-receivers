import sqlite3
import pandas as pd
import numpy as np
import statsmodels.stats.api as sm
from scipy import stats

cols = {'weight': 'Weight', 'height': 'Height', 'rec_per_game': "Receptions per Game",
     'yards_per_rec': 'Yards per Reception', 'catch_pct': 'Catch %',
     'targets_per_game': 'Targets per Game', 'rec_yards_per_game': 'Receiving Yards per Game',
       'td': 'Receiving Touchdowns'}

col_list = list(cols.keys())

def process_data():
    conn = sqlite3.connect("../data/processed/nfl_wr.db")
    df = pd.read_sql_query("select * from wide_receivers;", conn, index_col='index')
    conn.close()

    more_targets = df.loc[df['targets'] >= 3].copy()
    more_targets['tall'] = more_targets.loc[:, 'height'].apply(lambda x: 1 if x >= 75.0 else 0)

    return more_targets

def confidence_intervals(df):
    # 95% confidence intervals for tall and short mean values for all attributes in col_list
    with open('../models/inferential_confint.txt', 'w') as outfile:
        for col in col_list:
            tall_z = sm.DescrStatsW(df[df.tall == 1][col]).zconfint_mean(alpha = 0.025)
            short_z = sm.DescrStatsW(df[df.tall == 0][col]).zconfint_mean(alpha = 0.025)
            outfile.write(col)
            outfile.write("\n")
            outfile.write("short {0} \n".format(short_z))
            outfile.write("tall {0} \n \n".format(tall_z))

    return

def t_test(df):
    # perform independent t-tests for all metrics in col_list
    with open('../models/inferential_ttest.txt', 'w') as outfile:
        for col in col_list:
            two_sided_t = stats.ttest_ind(df[df.tall == 0][col],
                  df[df.tall == 1][col], equal_var = False)

            outfile.write(col)
            outfile.write("\n")
            outfile.write("{0} \n \n".format(two_sided_t))

    return
