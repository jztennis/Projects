from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import time
import csv
from datetime import date

### Get UTR Rating ###
def get_utr_rating(df):
    start = time.time()
    # Initialize the Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()

    count = 0
    with open('utr_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Gender', 'Nationality', 'UTR_S', 'UTR_D'])

        for i in range(len(df)):
            search_url = edit_url(df['city'][i+1], df['state_id'][i+1], df['lat'][i+1], df['lng'][i+1])
            if count > 0:
                break
            count += 1

            driver.get(search_url)

            scroll_count = 5

            for _ in range(scroll_count):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5) # Wait for the new results to load

            # Now that the page is rendered, parse the page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the UTR rating using an appropriate selector
            results = soup.find_all("div", class_="search__resultContainer__IxGRs")
            print(results)

            data = []
            i = 0
            for result in results:
                data.append([result.find("div", class_ = "name show-ellipsis").text])
                temp_places = result.find("span", class_ = "show-ellipsis d-block").text
                data[i].append(temp_places[0])
                data[i].append(temp_places[4:])
                # data[i].append(result.find("div", class_ = "value").text)
                verified = result.find_all("div", class_ = "value")
                # potential = result.find_all("div", class_ = "value text-lighter")
                # print(verified)
                # print(potential)

                no_utr = True
                utr_count = 0
                for j in range(len(verified)):
                    try:
                        # print(verified[j].text)
                        int(verified[j].text[0])
                        data[i].append(verified[j].text[:-1])
                        if utr_count == 1:
                            break
                        utr_count += 1
                        no_utr = True
                    except:
                        data[i].append('')
                    if verified[j].text is not None:
                        data[i].append(verified[j].text[:-1])
                    

                if no_utr:
                    data[i].append('')
                    data[i].append('')
                i += 1

            writer.writerows(data)

    # Close the driver
    driver.quit()

    end = time.time()
    print(f"Runtime: {round(end-start, 2)}s")
###

def edit_url(city, state, lat, long):
    d = str(date.today())
    d.replace('-', '/')

    url = f'https://app.utrsports.net/search?sportTypes=tennis,pickleball&startDate={d}&distance=10mi&utrMin=1&utrMax=16&utrType=verified&utrTeamType=singles&utrFitPosition=6&type=players&lat={lat}&lng={long}&locationInputValue={city},%20{state},%20USA&location={city},%20{state},%20USA' # initliaze url

    return url