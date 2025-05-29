from scraper import *
import pandas as pd
# from selenium.webdriver.chrome.options import Options

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

# options = Options().add_argument('--headless')
upcoming_matches = pd.read_csv('upcoming.csv')
# print(upcoming_matches)

with open('upcoming.csv', 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # writer.writerow(['tournament', 'p1', 'p1_odds', 'p2', 'p2_odds'])

    url = 'https://sportsbook.draftkings.com/sports/tennis'

    driver = webdriver.Chrome()
    driver.get(url)

    time.sleep(1)

    scroll_page(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tournaments = soup.find_all("div", class_="league-link")

    total = len(tournaments)/100
    count = 0
    for tournament in tournaments:
        count += 1
        print(f'Scraping..... {round(count/total)}%')
        tourney_name = tournament.find("div", class_="league-link__link-name").text
        try:
            tournament.find("div", class_="league-link__link-icons-sgp").text
        except:
            continue
        if tourney_name[:3] == 'ATP' or tourney_name[-2] == 'M':
            driver.find_element(By.LINK_TEXT, tourney_name).click()
            time.sleep(0.5)
            scroll_page(driver)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tournament_name = driver.current_url
            if 'doubles' in tournament_name:
                driver.get(url)
                time.sleep(0.5)
                scroll_page(driver)
                continue

            for i in range(len(tournament_name)):
                if tournament_name[-(i+1)] == '/':
                    tournament_name = tournament_name[-i:]
                    break
                # elif tournament_name[-(i+1)] == '-':
                #     print(tournament_name[:-(i+1)-1], tournament_name[:-i])
                #     tournament_name = tournament_name[:-(i+1)-1] + ' ' + tournament_name[:-i]
            # print(tournament_name)
            if 'atp' in tournament_name:
                tournament_name = tournament_name[4:]
            if 'qualifiers' in tournament_name:
                tournament_name = tournament_name[:-11]
            if 'men' in tournament_name:
                tournament_name = tournament_name[:-4]

            for i in range(len(tournament_name)):
                if tournament_name[i] == '-':
                    tournament_name = tournament_name[:i] + ' ' + tournament_name[i+1:]

            matches = soup.find_all("div", class_="sportsbook-event-accordion__children-wrapper")
            for match in matches:
                players = match.find_all("span", class_="sportsbook-outcome-cell__label")
                odds = match.find_all("span", class_="sportsbook-odds american default-color")
                # row = pd.Series([tournament_name, players[0].text, odds[0].text, players[1].text, odds[1].text], index=['tournament', 'p1', 'p1_odds', 'p2', 'p2_odds'])
                # if upcoming_matches.isin(row).all(axis=1).any():
                writer.writerow([tournament_name, players[0].text, odds[0].text, players[1].text, odds[1].text])
            driver.get(url)
            time.sleep(0.5)
            scroll_page(driver)
    driver.quit()
    print('DONE...')