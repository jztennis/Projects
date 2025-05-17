from scraper import *
import pandas as pd
import creds

profile_ids = pd.read_csv('profile_id.csv')

with open('utr_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['f_name', 'l_name', 'date', 'utr'])

    scrape_utr_history(profile_ids, creds.email, creds.password, offset=0, stop=50, writer=writer)