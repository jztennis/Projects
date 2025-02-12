from scraper import *
import pandas as pd
import creds

cities = pd.read_csv('cities.csv')
distinct_players = pd.read_csv('C:/Users/Jared/Dropbox/Code/Python/UTR_Project/names_and_urls/distinct_players.csv')
profile_ids = pd.read_csv('profile_id.csv')

user_input = input("Amateur Ratings: 'r' | Amateur Ratings Test: 't' | Pro Matches/UTRs: 'p' | UTR History: 'h' ...")

start = time.time()

if user_input == 'r':
    with open('utr_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        get_utr_rating(cities, creds.email, creds.password, offset=600, stop=1, writer=writer)

elif user_input == 't':
    with open('data_test.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        get_utr_rating_test(cities, creds.email, creds.password, offset=2992, stop=1, writer=writer)

elif user_input == 'p':
    with open('player_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['tourney_date', 'p1_name', 'p1_utr', 'p2_name', 'p2_utr', 'p1_games_won', 'p2_games_won', 'score', 'winner'])

        scrape_player_utr(distinct_players, creds.email, creds.password, offset=50, stop=1, writer=writer)

elif user_input == 'h':
    with open('utr_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['f_name', 'l_name', 'date', 'utr'])

        scrape_utr_history(profile_ids, creds.email, creds.password, offset=0, stop=10, writer=writer)

end = time.time()
print(f"Runtime: {round(end-start, 2)}s") # print runtime