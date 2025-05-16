from scraper import *
import pandas as pd
import creds

'''
14929 Rows in atp_utr_tennis_matches.csv (ORIGINAL)
'''

def get_player_history(utr_history):
    history = {}
    # print(len(utr_history))
    for i in range(len(utr_history)):
        # print(utr_history['f_name'][i], utr_history['l_name'][i])
        if utr_history['f_name'][i]+' '+utr_history['l_name'][i] not in history.keys():
            history[utr_history['f_name'][i]+' '+utr_history['l_name'][i]] = [[utr_history['utr'][i], utr_history['date'][i]]]
        else:
            history[utr_history['f_name'][i]+' '+utr_history['l_name'][i]].append([utr_history['utr'][i], utr_history['date'][i]])
    return history

profile_ids = pd.read_csv('profile_id.csv')
utr_history = pd.read_csv('utr_history.csv')
prev_matches = pd.read_csv('atp_utr_tennis_matches.csv')
utr_history = get_player_history(utr_history)

with open('atp_utr_tennis_matches.csv', 'a', newline='', encoding='utf-8') as csvfile:
    print("Scraping...")
    writer = csv.writer(csvfile)
    scrape_player_matches(profile_ids, utr_history, prev_matches, creds.email, creds.password, offset=0, stop=-1, writer=writer)

print('DONE...')

matches = pd.read_csv('atp_utr_tennis_matches.csv')
matches.drop_duplicates(subset=['date','p1','p2'])
matches.to_csv('atp_utr_tennis_matches.csv', index=False)