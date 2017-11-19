from data.make_dataset import *
from visualization.visualize import *
from models.inferential import *
from models.regression import *

if __name__ == "__main__":
    print("")
    print("This program conducts analysis on NFL wide recievers.")
    print("")

    # Scraping data and storing it into pickle files and a SQL DB
    start = int(input("What season (year) would you like to start at? "))
    end = int(input("What season (year) would you like to end at? "))
    print("")
    print("Beginining to scrape season statistics.")
    print("")
    stats = scrape_stats(start, end)
    print("")
    print("Season statistics scraping is complete and the raw data is stored in a pickle file.")
    print("")
    print("Beginining to scrape individual player demographics.")
    print("")
    players = scrape_players(stats)
    print("")
    print("Player demographics scraping is complete and the raw data is stored in a pickle file.")
    print("")
    print("Cleaning data, formatting units, and so much other fun stuff going on!")
    cleaned_df = clean_data_store_sql(players)
    print("Done cleaning data.")
    print("")

    # Inferential analysis
    choice = input("Do you want to run the inferential analysis? (Y or N) ")

    if choice == "Y":
        print("")
        print("Importing and processing data")
        print("")
        data = process_data()
        print("Running inferential analysis. See output files")
        print("")
        confidence_intervals(data)
        t_test(data)
        print("Inferential analysis complete.")
        print("")

    # Regression analysis
    choice = input("Do you want to run the regression analysis? (Y or N) ")

    if choice == "Y":
        print("")
        print("Importing and processing data")
        print("")
        data = process_data()
        num_cols = len(data.columns)
        choice = int(input("We shall use best subset selection. How many features would you like? (There are {0}) ".format(num_cols)))
        print("")
        print("Running regression analysis. See output files")
        print("")
        run_model(data, choice)
        print("")
        print("Regression analysis complete.")
        print("")

    print("Program complete.")
    print("")
