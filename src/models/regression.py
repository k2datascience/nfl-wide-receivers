import sqlite3
import pandas as pd
import numpy as np
import statsmodels.api as sm
import itertools
import time
import pickle

def processSubset(feature_set, X, y):
    # Fit model on feature_set and calculate RSS
    model = sm.OLS(y, X[list(feature_set)].astype(float))
    regr = model.fit()
    RSS = ((regr.predict(X[list(feature_set)]) - y) ** 2).sum()
    return {"model":regr, "RSS":RSS}

# get best features combination
def getBest(k, X, y):

    tic = time.time()

    results = []

    # iterate over all possible k-sized combinations of features
    # then model each and append results
    for combo in itertools.combinations(X.columns, k):
        results.append(processSubset(combo, X, y))

    # Wrap everything up in a nice dataframe
    models = pd.DataFrame(results)

    # Choose the model with the lowest RSS
    best_model = models.loc[models['RSS'].idxmin()]

    toc = time.time()
    print("Processed ", models.shape[0], "models on", k, "predictors in", (toc-tic), "seconds.")

    # Return the best model, along with some other useful information about the model
    return best_model


def run_model(df, feature_count):
    df = df.drop(['demo_link', 'name', 'team', 'position'], axis=1)

    y = df.td
    X = df.drop(['td', 'catch_pct', 'age', 'targets_per_game', 'rec_yards_per_game', 'rec_per_game', 'height'], axis=1)

    models = pd.DataFrame(columns=["RSS", "model"])

    tic = time.time()

    # iterate over combination sizes 1 to 10
    for i in range(1, feature_count):
        models.loc[i] = getBest(i, X, y)

    toc = time.time()
    print("Total elapsed time:", (toc-tic), "seconds.")

    pickle.dump(models, open("../models/regression_subsets.p", "wb"))

    return models
