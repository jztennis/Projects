from scraper import *
import pandas as pd
import creds

cities = pd.read_csv('cities.csv')
distinct_players = pd.read_csv('distinct_players.csv')
'''
CONFIG:
    - offset = starting point in the cities.csv dataset
    - stop = number of pages to scrape before stopping

    - offset_test = start point in cities.csv dataset for test function
    - stop_test = num pages to scrape before stopping for test function

    - player_stop = num player profles to scrape before stopping
'''
offset = 600
stop = 1 # MAKE SURE: stop >= 1 (600 = ~1-1.5 hr)

offset_test = 2992
stop_test = 1

player_stop = 100

start = time.time()

# get_utr_rating(cities, creds.email, creds.password, offset=offset, stop=stop)
# get_utr_rating_test(cities, creds.email, creds.password, offset=offset_test, stop=stop_test)
scrape_player_utr(distinct_players, creds.email, creds.password, stop=player_stop)

end = time.time()
print(f"Runtime: {round(end-start, 2)}s") # print runtime