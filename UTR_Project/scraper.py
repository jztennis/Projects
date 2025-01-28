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

    - Has nothing to do with Denver, CO
    - MAIN PROBLEM:
        *Attempting to use a delegate that only supports static-sized tensors with a graph that has dynamic-sized tensors

    - ABOVE ERROR SEEMINGLY FIXED BY ADDING (encoding='utf-8') TO LINE THAT IS with open(utr_data.csv...)
'''

### Get UTR Rating ###
def get_utr_rating(df, offset, stop):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()

    driver.get('https://app.utrsports.net/') # login page

    time.sleep(1) # wait to load

    # finds boxes on webpage
    username = driver.find_element(By.ID, "emailInput")
    password = driver.find_element(By.ID, "passwordInput")
    login_button = driver.find_element(By.XPATH, '//*[@id="myutr-app-body"]/div/div/div/div/div/div[2]/form/div[3]/button')

    username.send_keys('jz1352@gmail.com') # enter email here
    password.send_keys('Mr.Milom0nst3r!%') # enter password here
    time.sleep(0.5)
    login_button.click() # clicks button

    time.sleep(2.5) # if getting signed out increase sleep timer

    # CONFIG:
    count = 0
    date_today = str(date.today())

    with open('utr_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
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
            i = 0
            for result in results:
                data.append([result.find("div", class_ = "name show-ellipsis").text]) # player name
                temp_places = result.find("span", class_ = "show-ellipsis d-block").text
                data[i].append(temp_places[0]) # player gender
                data[i].append(temp_places[4:]) # player location
                verified = result.find_all("div", class_ = "value") # player UTRs

                utr_count = 0
                num = 0
                for j in range(len(verified)):
                    try: # nums could be 11.xx so try except is needed
                        int(verified[j].text[0])
                        num += 1
                        if verified[j].text[:-1] not in data[i] or num == 2:
                            if utr_count != 2:
                                data[i].append(verified[j].text[:-1])
                                utr_count += 1
                            else:
                                break
                        if utr_count == 2:
                            break
                    except: # not a number
                        if utr_count == 2:
                            break
                        data[i].append('') # utr is blank here
                        utr_count += 1

                data[i].append(date_today)
                i += 1

            writer.writerows(data) # write to utr_data.csv

    # Close the driver
    driver.quit()
###

def edit_url(city, state, lat, long):
    d = str(date.today())
    d.replace('-', '/')

    url = f'https://app.utrsports.net/search?sportTypes=tennis,pickleball&startDate={d}&distance=10mi&utrMin=1&utrMax=16&utrType=verified&utrTeamType=singles&utrFitPosition=6&type=players&lat={lat}&lng={long}&locationInputValue={city},%20{state},%20USA&location={city},%20{state},%20USA' # initliaze url

    return url

### Get UTR Rating ###
def get_utr_rating_test(df, offset, stop):
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()

    driver.get('https://app.utrsports.net/') # login page

    time.sleep(1) # wait to load

    # finds boxes on webpage
    username = driver.find_element(By.ID, "emailInput")
    password = driver.find_element(By.ID, "passwordInput")
    login_button = driver.find_element(By.XPATH, '//*[@id="myutr-app-body"]/div/div/div/div/div/div[2]/form/div[3]/button')

    username.send_keys('email') # enter email here
    password.send_keys('password') # enter password here
    time.sleep(0.5)
    login_button.click() # clicks button

    time.sleep(2.5) # if getting signed out increase sleep timer

    # CONFIG:
    count = 0
    offset = 2992
    stop = 1 # MAKE SURE: stop >= 1 (600 = ~1-1.5 hr)
    date_today = str(date.today())

    with open('data_test.csv', 'a', newline='', encoding='utf-8') as csvfile:
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
            i = 0
            for result in results:
                data.append([result.find("div", class_ = "name show-ellipsis").text]) # player name
                temp_places = result.find("span", class_ = "show-ellipsis d-block").text
                data[i].append(temp_places[0]) # player gender
                data[i].append(temp_places[4:]) # player location
                verified = result.find_all("div", class_ = "value") # player UTRs

                utr_count = 0
                num = 0
                for j in range(len(verified)):
                    try: # nums could be 11.xx so try except is needed
                        int(verified[j].text[0])
                        num += 1
                        if verified[j].text[:-1] not in data[i] or num == 2:
                            if utr_count != 2:
                                data[i].append(verified[j].text[:-1])
                                utr_count += 1
                            else:
                                break
                        if utr_count == 2:
                            break
                    except: # not a number
                        if utr_count == 2:
                            break
                        data[i].append('') # utr is blank here
                        utr_count += 1

                data[i].append(date_today)
                i += 1

            writer.writerows(data) # write to utr_data.csv

    # Close the driver
    driver.quit()
###