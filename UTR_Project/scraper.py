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
    login_button = driver.find_element(By.XPATH, '//*[@id="myutr-app-body"]/div/div/div/div/div/div[2]/form/div[3]/button')

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

### Get UTR Rating ###
def get_utr_rating(df, email, password, offset=0, stop=1):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()
    url = 'https://app.utrsports.net/'

    sign_in(driver, url, email, password)

    # CONFIG:
    count = 0
    date_today = str(date.today())

    csvfile = open('utr_data.csv', 'a', newline='', encoding='utf-8')

    writer = csv.writer(csvfile)
    # writer.writerow(['Name', 'Gender', 'Nationality', 'UTR_S', 'UTR_D', 'Pull_Date'])

    for i in range(len(df)):
        search_url = edit_url(df['city'][i+offset], df['state_id'][i+offset], df['lat'][i+offset], df['lng'][i+offset])
        if count > stop-1: # num of pages to scrape -1
            break
        count += 1

        driver.get(search_url)

        scroll_count = 5 # num of scrolls to load page

        # scroll the page
        for _ in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5) # Wait for the new results to load

        # Now that the page is rendered, parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the UTR rating using an appropriate selector
        results = soup.find_all("div", class_="search__resultContainer__IxGRs")

        data = []
        k = 0
        for result in results:
            data.append([result.find("div", class_ = "name show-ellipsis").text]) # player name
            temp_places = result.find("span", class_ = "show-ellipsis d-block").text
            data[k].append(temp_places[0]) # player gender
            data[k].append(temp_places[4:]) # player location
            verified = result.find_all("div", class_ = "value") # player UTRs

            utr_count = 0
            num = 0
            for j in range(len(verified)):
                try: # nums could be 11.xx so try except is needed
                    int(verified[j].text[0])
                    num += 1
                    if verified[j].text[:-1] not in data[k] or num == 2:
                        if utr_count != 2:
                            data[k].append(verified[j].text[:-1])
                            utr_count += 1
                        else:
                            break
                    if utr_count == 2:
                        break
                except: # not a number
                    if utr_count == 2:
                        break
                    data[k].append('') # utr is blank here
                    utr_count += 1

            data[k].append(date_today)
            k += 1

        writer.writerows(data) # write to utr_data.csv

    # Close the driver
    driver.quit()
###

### Get UTR Rating Tester Function ###
def get_utr_rating_test(df, email, password, offset=0, stop=1):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()
    url = 'https://app.utrsports.net/'

    sign_in(driver, url, email, password)

    # CONFIG:
    count = 0
    date_today = str(date.today())

    csvfile = open('data_test.csv', 'a', newline='', encoding='utf-8')

    writer = csv.writer(csvfile)
    # writer.writerow(['Name', 'Gender', 'Nationality', 'UTR_S', 'UTR_D', 'Pull_Date'])

    for i in range(len(df)):
        search_url = edit_url(df['city'][i+offset], df['state_id'][i+offset], df['lat'][i+offset], df['lng'][i+offset])
        if count > stop-1: # num of pages to scrape -1
            break
        count += 1

        driver.get(search_url)

        scroll_count = 5 # num of scrolls to load page

        # scroll the page
        for _ in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5) # Wait for the new results to load

        # Now that the page is rendered, parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the UTR rating using an appropriate selector
        results = soup.find_all("div", class_="search__resultContainer__IxGRs")

        data = []
        k = 0
        for result in results:
            data.append([result.find("div", class_ = "name show-ellipsis").text]) # player name
            temp_places = result.find("span", class_ = "show-ellipsis d-block").text
            data[k].append(temp_places[0]) # player gender
            data[k].append(temp_places[4:]) # player location
            verified = result.find_all("div", class_ = "value") # player UTRs

            utr_count = 0
            num = 0
            for j in range(len(verified)):
                try: # nums could be 11.xx so try except is needed
                    int(verified[j].text[0])
                    num += 1
                    if verified[j].text[:-1] not in data[k] or num == 2:
                        if utr_count != 2:
                            data[k].append(verified[j].text[:-1])
                            utr_count += 1
                        else:
                            break
                    if utr_count == 2:
                        break
                except: # not a number
                    if utr_count == 2:
                        break
                    data[k].append('') # utr is blank here
                    utr_count += 1

            data[k].append(date_today)
            k += 1

        writer.writerows(data) # write to utr_data.csv

    # Close the driver
    driver.quit()
###

### Get UTR Rating ###
def scrape_player_utr(df, email, password, stop=1):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()
    url = 'https://app.utrsports.net/'

    sign_in(driver, url, email, password)

    # CONFIG:
    count = 0
    date_today = str(date.today())

    csvfile = open('player_data.csv', 'w', newline='', encoding='utf-8')

    writer = csv.writer(csvfile)
    writer.writerow(['tourney_date', 'p1_name', 'p1_utr', 'p2_name', 'p2_utr', 'score', 'p1_games_won', 'p2_games_won', 'winner'])

    for i in range(len(df)):
        if count > stop - 1: # num of pages to scrape -1
            break
        count += 1

        search_url = f"https://app.utrsports.net/search?query={df['Name'][i+9][:-3]}%20{df['Name'][i+9][-2]}&sportTypes=tennis,pickleball&startDate={date_today}&utrMin=1&utrMax=16&utrType=verified&utrTeamType=singles&utrFitPosition=6&type=players&lat=47.16315729999999&lng=-122.0267787"


        driver.get(search_url)

        temp = True
        try: # Player Exists
            time.sleep(1)
            player = driver.find_element(By.XPATH, '//*[@id="myutr-app-body"]/div[1]/div[3]/div[2]/div[2]/div[2]/a')
            player.click()
            time.sleep(2)

        except: # Player Does Not Exist (Throws Error)
            temp = False
            
        if temp:
            scroll_count = 5 # num of scrolls to load page

            # scroll the page
            for _ in range(scroll_count):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5) # Wait for the new results to load

            # Now that the page is rendered, parse the page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            data = []
            z = 0
            tournaments = soup.find_all("div", class_="eventItem__eventItem__2Xpsd")
            name_ref = soup.find("h1", class_="headerV3__playerName__1mnMa").text
            for tourney in tournaments:
                tourney_start_date = tourney.find("div", class_="col-5 col-md-3 eventItem__eventTime__3U8ST").text
                tourney_start_date = tourney_start_date[:6]
                matches = tourney.find_all("div", class_="d-none d-md-block")
                for match in matches:
                    data.append([tourney_start_date])
                    winner_name = match.find("a", class_="flex-column player-name winner").text
                    loser_name = match.find("a", class_="flex-column player-name").text
                    utrs = match.find_all("div", class_="utr")
                    all_scores = match.find_all("div", "score-item")
                    score = ''
                    p1_games = 0
                    p2_games = 0
                    for i in range(int(len(all_scores) / 2)):
                        if len(all_scores[i].text) == 1:
                            score = score + all_scores[i].text + '-' + all_scores[i+(int(len(all_scores) / 2))].text + ' '
                            p1_games += int(all_scores[i].text)
                            p2_games += int(all_scores[i+(int(len(all_scores) / 2))].text)
                        else:
                            score = score + all_scores[i].text[0] + '(' + all_scores[i].text[1:] + ')-' + all_scores[i+(int(len(all_scores) / 2))].text[0] + '(' + all_scores[i+(int(len(all_scores) / 2))].text[1:] + ') '
                            p1_games += int(all_scores[i].text[0])
                            p2_games += int(all_scores[i+int(len(all_scores) / 2)].text[0])
                    score = score[:-1]

                    if winner_name == name_ref:     # profile player won
                        data[z].append(winner_name)
                        data[z].append(utrs[0].text[:-1])
                        data[z].append(loser_name)
                        data[z].append(utrs[1].text[:-1])
                        data[z].append(p1_games)
                        data[z].append(p2_games)
                        data[z].append(score)
                        data[z].append(0)
                    else:                           # profile player lost
                        data[z].append(loser_name)
                        data[z].append(utrs[0].text[:-1])
                        data[z].append(winner_name)
                        data[z].append(utrs[1].text[:-1])
                        data[z].append(p1_games)
                        data[z].append(p2_games)
                        data[z].append(score)
                        data[z].append(1)

                    z += 1


            writer.writerows(data)

    # Close the driver
    driver.quit()
###