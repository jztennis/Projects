# import requests
# import numpy as np
# from bs4 import BeautifulSoup

# # Making a GET request
# r = requests.get('https://app.utrsports.net/search?sportTypes=tennis,pickleball&startDate=08/04/2024&distance=10mi&utrMin=1&utrMax=16&utrType=verified&utrTeamType=singles&utrFitPosition=6&type=players&lat=47.16315729999999&lng=-122.0267787&locationInputValue=Buckley,%20WA,%20USA&location=Buckley,%20WA,%20USA')

# # Parsing the HTML
# soup = BeautifulSoup(r.content, 'html.parser')
# print(soup.prettify())
# print(soup)

# s = soup.find('div', style_='z-index: initial;')
# print(s)
# content = s.find_all('div')

# print(content)

import requests
from bs4 import BeautifulSoup

def get_utr_rating(player_name):
    # URL of the UTR player search page (Note: this URL may not be correct and is used for illustrative purposes)
    search_url = "https://app.utrsports.net/search?sportTypes=tennis,pickleball&startDate=08/29/2024&distance=10mi&utrMin=1&utrMax=16&utrType=verified&utrTeamType=singles&utrFitPosition=6&type=players&locationInputValue=Buckley,%20WA,%20USA&location=Buckley,%20WA,%20USA&lat=47.16315729999999&lng=-122.0267787"

    # Make a request to the UTR site
    response = requests.get(search_url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to retrieve the page")
        return None

    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the player's UTR rating (this selector is illustrative and may need adjustment)
    player_div = soup.find('div', class_ = "value text-lighter")  # Example class name
    print(player_div)
    if player_div:
        rating_span = player_div.find('span', class_='utr-rating')  # Example class name
        if rating_span:
            rating = rating_span.text.strip()
            return rating
        else:
            print("Rating not found")
            return None
    else:
        print("Player not found")
        return None

# Example usage
player_name = "Jared Zaugg"  # Replace with the name of the player you're searching for
rating = get_utr_rating(player_name)
# if rating:
#     print(f"{player_name}'s UTR rating is: {rating}")
# else:
#     print("Could not retrieve UTR rating")
