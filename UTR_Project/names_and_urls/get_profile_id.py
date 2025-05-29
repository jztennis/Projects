import pandas as pd
import csv
from scraper_copy import *
import creds_copy

df = pd.read_csv('distinct_players.csv')

date_today = str(date.today())

with open('profile_id.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['f_name', 'l_name', 'p_id'])

    driver = webdriver.Chrome()

    url = 'https://app.utrsports.net/'

    sign_in(driver, url, creds_copy.email, creds_copy.password)

    # stop = 1
    for i in range(len(df)):
        # if i == stop:
        #     break
        search_url = f"https://app.utrsports.net/search?query={df['f_name'][i]}%20{df['l_name'][i]}&sportTypes=tennis,pickleball&startDate={date_today}&utrMin=1&utrMax=16&utrType=verified&utrTeamType=singles&utrFitPosition=6&type=players&lat=47.16315729999999&lng=-122.0267787"

        load_page(driver, search_url)

        try:
            profile_id = driver.find_element(By.XPATH, '//*[@id="myutr-app-body"]/div[1]/div[3]/div[2]/div[2]/div[2]/a').get_attribute('href')
            row = [df['f_name'][i], df['l_name'][i], profile_id[35:]]
        except:
            profile_id = ''
            row = [df['f_name'][i], df['l_name'][i], profile_id]

        writer.writerow(row)