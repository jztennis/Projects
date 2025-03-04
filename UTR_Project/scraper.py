from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import time
import csv
from datetime import date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np

'''
NOTES:
    - Scraper can't go past Denver, CO (19th row in cities.csv). Gives error:
        * DevTools listening on ws://127.0.0.1:61306/devtools/browser/3da6171b-a2e7-40ec-88a5-55c69b3d4dfa
        * Created TensorFlow Lite XNNPACK delegate for CPU.
        * [24276:6160:0123/230738.058:ERROR:ssl_client_socket_impl.cc(878)] handshake failed; returned -1, SSL error code 1, net_error -101
        * [24276:6160:0123/230738.103:ERROR:ssl_client_socket_impl.cc(878)] handshake failed; returned -1, SSL error code 1, net_error -100
        * Attempting to use a delegate that only supports static-sized tensors with a graph that has dynamic-sized tensors (tensor#58 is a dynamic-sized tensor).
        * Traceback (most recent call last):
        * ...
'''

### Sign In UTR ###
def sign_in(driver, log_in_url, email, password):
    driver.get(log_in_url)

    time.sleep(1)

    email_box = driver.find_element(By.ID, 'emailInput')
    password_box = driver.find_element(By.ID, 'passwordInput')
    login_button = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary.btn-xl.btn-block')

    email_box.send_keys(email) # enter email here
    password_box.send_keys(password) # enter password here
    time.sleep(0.5)
    login_button.click() # clicks button

    time.sleep(2.5) # if getting signed out increase sleep timer

### URL Modification ###
def edit_url(city, state, lat, long):
    d = str(date.today())
    d.replace('-', '/')

    url = f'https://app.utrsports.net/search?sportTypes=tennis,pickleball&startDate={d}&distance=10mi&utrMin=1&utrMax=16&utrType=verified&utrTeamType=singles&utrFitPosition=6&type=players&lat={lat}&lng={long}&locationInputValue={city},%20{state},%20USA&location={city},%20{state},%20USA' # initliaze url

    return url
###

### Formats Match Scores ###
def collect_scores(all_scores):
    score = ''
    p1_games = 0
    p2_games = 0
    for i in range(int(len(all_scores) / 2)):
        if len(all_scores[i].text) == 1:
            score = score + all_scores[i].text + '-' + all_scores[i+(int(len(all_scores) / 2))].text + ' '
            p1_games += int(all_scores[i].text)
            p2_games += int(all_scores[i+(int(len(all_scores) / 2))].text)
        else:
            score = score + all_scores[i].text[0] + '-' + all_scores[i+(int(len(all_scores) / 2))].text[0] + ' '
            p1_games += int(all_scores[i].text[0])
            p2_games += int(all_scores[i+int(len(all_scores) / 2)].text[0])
    score = score[:-1]
    return score, p1_games, p2_games
###

### Loads The Page ###
def load_page(driver, url):
    driver.get(url)
    time.sleep(1)
###

### Scrolls The Page ###
def scroll_page(driver):
    previous_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == previous_height:
            break
        previous_height = new_height
###

### Get UTR Rating ###
def get_utr_rating(df, email, password, offset=0, stop=1, writer=None):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()
    url = 'https://app.utrsports.net/'

    sign_in(driver, url, email, password)

    # CONFIG:
    count = 0
    date_today = str(date.today())

    for i in range(len(df)):
        search_url = edit_url(df['city'][i+offset], df['state_id'][i+offset], df['lat'][i+offset], df['lng'][i+offset])
        if count > stop-1: # num of pages to scrape -1
            break
        count += 1

        load_page(driver, search_url)

        scroll_page(driver)

        # Now that the page is rendered, parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all("div", class_="search__resultContainer__IxGRs")

        for result in results:
            data_row = [result.find("div", class_="name show-ellipsis").text]
            temp_places = result.find("span", class_ = "show-ellipsis d-block").text
            verified = result.find_all("div", class_ = "value") # player UTRs

            data_row += [temp_places[0], temp_places[4:]]

            utr_count = 0
            num = 0
            for j in range(len(verified)):
                try:
                    int(verified[j].text[0])
                    num += 1
                    if verified[j].text[:-1] not in data_row or num == 2:
                        if utr_count != 2:
                            data_row += [verified[j].text[:-1]]
                            utr_count += 1
                        else:
                            break
                    if utr_count == 2:
                        break
                except:
                    if utr_count == 2:
                        break
                    data_row += ['']
                    utr_count += 1

            data_row += [date_today]

            writer.writerow(data_row)

    # Close the driver
    driver.quit()
###

### Get UTR Rating Tester Function ###
def get_utr_rating_test(df, email, password, offset=0, stop=1, writer=None):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()
    url = 'https://app.utrsports.net/'

    sign_in(driver, url, email, password)

    # CONFIG:
    count = 0
    date_today = str(date.today())

    for i in range(len(df)):
        search_url = edit_url(df['city'][i+offset], df['state_id'][i+offset], df['lat'][i+offset], df['lng'][i+offset])
        if count > stop-1: # num of pages to scrape -1
            break
        count += 1

        load_page(driver, search_url)

        scroll_page(driver)

        # Now that the page is loaded, get the containers
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all("div", class_="search__resultContainer__IxGRs")

        for result in results:
            data_row = [result.find("div", class_="name show-ellipsis").text]
            temp_places = result.find("span", class_ = "show-ellipsis d-block").text
            verified = result.find_all("div", class_ = "value") # player UTRs

            data_row += [temp_places[0], temp_places[4:]]

            utr_count = 0
            num = 0
            for j in range(len(verified)):
                try:
                    int(verified[j].text[0])
                    num += 1
                    if verified[j].text[:-1] not in data_row or num == 2:
                        if utr_count != 2:
                            data_row += [verified[j].text[:-1]]
                            utr_count += 1
                        else:
                            break
                    if utr_count == 2:
                        break
                except:
                    if utr_count == 2:
                        break
                    data_row += ['']
                    utr_count += 1

            data_row += [date_today]

            writer.writerow(data_row)

    # Close the driver
    driver.quit()
###

### Get UTR Rating ###
def scrape_player_utr(df, email, password, offset=0, stop=1, writer=None):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()
    url = 'https://app.utrsports.net/'

    sign_in(driver, url, email, password)

    count = 0
    date_today = str(date.today())

    for i in range(len(df)):
        if count > stop - 1:
            break
        count += 1

        search_url = f"https://app.utrsports.net/search?query={df['Name'][i+offset][:-3]}%20{df['Name'][i+offset][-2]}&sportTypes=tennis,pickleball&startDate={date_today}&utrMin=1&utrMax=16&utrType=verified&utrTeamType=singles&utrFitPosition=6&type=players&lat=47.16315729999999&lng=-122.0267787"

        load_page(driver, search_url)

        try: # Player Exists
            player = driver.find_element(By.XPATH, '//*[@id="myutr-app-body"]/div[1]/div[3]/div[2]/div[2]/div[2]/a')
            player.click()
            time.sleep(2)

        except: # Player Does Not Exist (Throws Error)
            continue
            
        scroll_page(driver)

        # Now that the page is rendered, parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tournaments = soup.find_all("div", class_="eventItem__eventItem__2Xpsd")

        '''
        try except fixes: "AttributeError: 'NoneType' object has no attribute 'text'"
        '''
        try:
            name_ref = soup.find("h1", class_="headerV3__playerName__1mnMa").text
        except:
            name_ref = driver.find_element(By.XPATH, '//*[@id="myutr-app-body"]/div/div[1]/div[1]/div/div/div/div[1]/div[1]/div[2]/h1').text

        '''
        For each tournament, grab the data specified from each match in the tournament.
        Rework some data based on winners vs losers and errors that need exceptions.
        '''
        for tourney in tournaments:
            tourney_start_date = tourney.find("div", class_="col-5 col-md-3 eventItem__eventTime__3U8ST").text[:6]
            matches = tourney.find_all("div", class_="d-none d-md-block")

            for match in matches:
                data_row = [tourney_start_date]
                is_tie = False

                try:
                    winner_name = match.find("a", class_="flex-column player-name winner").text # throws error when TIE (COLLEGE MATCHES)
                    loser_name = match.find("a", class_="flex-column player-name").text
                except:
                    tie = match.find_all("a", class_="flex-column player-name")
                    winner_name, loser_name = tie[0].text, tie[1].text
                    is_tie = True

                utrs = match.find_all("div", class_="utr")
                all_scores = match.find_all("div", "score-item")
                score, p1_games, p2_games = collect_scores(all_scores)
                score = score if score else 'W'

                if winner_name == name_ref:
                    data_row += [winner_name, utrs[0].text[:-1], loser_name, utrs[1].text[:-1], p1_games, p2_games, score, 1]
                else:
                    data_row += [loser_name, utrs[0].text[:-1], winner_name, utrs[1].text[:-1], p1_games, p2_games, score, 0]

                if is_tie:
                    data_row[-1] = 0.5  # Mark ties properly

                writer.writerow(data_row)

    # Close the driver
    driver.quit()
###

### Get UTR History ###
def scrape_utr_history(df, email, password, offset=0, stop=1, writer=None):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()
    url = 'https://app.utrsports.net/'

    sign_in(driver, url, email, password)

    for i in range(len(df)):
        if i == stop:
            break
        
        try:
            search_url = f"https://app.utrsports.net/profiles/{round(df['p_id'][i+offset])}?t=6"
        except:
            continue

        load_page(driver, search_url)

        time.sleep(0.25)

        scroll_page(driver)

        try:
            time.sleep(1)
            show_all = driver.find_element(By.LINK_TEXT, 'Show all')
            show_all.click()
        except:
            try:
                time.sleep(2)
                show_all = driver.find_element(By.LINK_TEXT, 'Show all')
                show_all.click()
            except:
                print(f"{df['f_name'][i]} | {df['l_name'][i]} | {df['p_id'][i]}")
                continue

        time.sleep(1)

        scroll_page(driver)

        # Now that the page is rendered, parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        container = soup.find("div", class_="newStatsTabContent__section__1TQzL p0 bg-transparent")
        
        utrs = container.find_all("div", class_="row")
        
        for j in range(len(utrs)):
            if j == 0:
                continue
            utr = utrs[j].find("div", class_="newStatsTabContent__historyItemRating__GQUXw").text
            utr_date = utrs[j].find("div", class_="newStatsTabContent__historyItemDate__jFJyD").text

            data_row = [df['f_name'][i+offset], df['l_name'][i+offset], utr_date, utr]

            writer.writerow(data_row)

    # Close the driver
    driver.quit()
###