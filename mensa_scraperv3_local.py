import requests
from bs4 import BeautifulSoup
import collections
from fake_useragent import UserAgent
import traceback
import json
import re
import schedule
import time
import datetime
from timeit import default_timer as timer
from pprint import pprint

def start_scrape_mensa(mensa=False, rote_beete=False):
    try:
        ua = UserAgent()
        user_agent = ua.random
    except:
        print("[-] Error with User-Agent taking a default one")
        user_agent = "Mozilla/5.0 (Linux; Android 5.1.1; D2533 Build/19.4.A.0.182) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36"

    headers = {"User-Agent": user_agent}

    if mensa:
        url = 'https://www.akafoe.de/gastronomie/speiseplaene-der-mensen/ruhr-universitaet-bochum'
    elif rote_beete:
        url = "https://www.akafoe.de/gastronomie/speiseplaene-der-mensen/rote-bete"


    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    dish_list = soup.find_all("div", {"class": "row list-dish"})

    day_list = soup.find("div", {"class": "week"})
    day_list_list = []

    wochen_speiseplan = collections.defaultdict(dict)

    for day in day_list:
        date = day.text.strip()
        if date:
            day_list_list.append(date)

    i = 0

    for dish_day in dish_list:

        items = list(dish_day.find_all("div", {"class": "item"}))
        types = collections.defaultdict(dict)

        title = None
        price = None
        allergies = None

        for item in items:

            sibling = item.find_previous_sibling('h3').text.strip()

            try:
                title = item.find("h4").text.strip()
            except Exception:
                traceback.print_exc()
            try:
                price = item.find("div", {"class": "price"}).text.strip()
            except Exception:
                if mensa:
                    traceback.print_exc()
            try:
                allergies = item.find("small").text.strip()
            except Exception:
                traceback.print_exc()

            try:
                title = title.replace(allergies, "").strip()
            except Exception:
                traceback.print_exc()

            if types[sibling]:
                types[sibling].append({"title": title, "price": price, "allergies": allergies})
            else:
                types[sibling] = [{"title": title, "price": price, "allergies": allergies}]

        wochen_speiseplan[day_list_list[i]] = types

        i += 1

    return wochen_speiseplan


def scrape_qwest():
    url = "https://q-we.st/speiseplan/"

    try:
        ua = UserAgent()
        user_agent = ua.random
    except:
        print("[-] Error with User-Agent taking a default one")
        user_agent = "Mozilla/5.0 (Linux; Android 5.1.1; D2533 Build/19.4.A.0.182) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36"

    headers = {"User-Agent": user_agent}

    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    ALL_DATES = soup.find_all("span", {"class": "live_speiseplan_title"})
    ALL_TITLES = soup.find_all("span", {"class": "live_speiseplan_item_title"})
    ALL_TAGS = soup.find_all("sup", {"class": "live_speiseplan_item_kennzeichen"})
    ALL_PRICES = soup.find_all("span", {"class": "live_speiseplan_item_price"})

    wochen_speiseplan = collections.defaultdict(dict)

    all_dates_list = []

    days = ["Mo,", "Di,", "Mi,", "Do,", "Fr,"]

    try:
        for i, date in enumerate(ALL_DATES):
            string = date.text.strip()
            actual_date = re.search(r'\d{2}.\d{2}.', string) #and directly in our form we had in mensa scrape
            #assuming here that date will always start with monday and ends with friday
            our_format = f'{days[i]} {actual_date[0]}'
            all_dates_list.append(our_format)
    except IndexError:
        traceback.print_exc()
    except Exception:
        traceback.print_exc()


    DAY_SPEISEN = soup.find_all("div", {"class": "live_speiseplan_items"})

    try:
        for i, DAY_SPEISE in enumerate(DAY_SPEISEN):
            ALL_TITLES = DAY_SPEISE.find_all("span", {"class": "live_speiseplan_item_title"})
            ALL_TAGS = DAY_SPEISE.find_all("sup", {"class": "live_speiseplan_item_kennzeichen"})
            ALL_PRICES = DAY_SPEISE.find_all("span", {"class": "live_speiseplan_item_price"})

            #popping them here out weil erste title und price der verwendet wird is leer
            ALL_TITLES.pop(0)
            ALL_PRICES.pop(0)

            MEAL_LIST = []

            for meal_i in range(0, len(ALL_TITLES)):
                meal = {"title": ALL_TITLES[meal_i].text.replace(ALL_TAGS[meal_i].text, "").strip(), "price": ALL_PRICES[meal_i].text.strip(), "allergies": ALL_TAGS[meal_i].text.strip()}
                MEAL_LIST.append(meal)

            wochen_speiseplan[all_dates_list[i]] = MEAL_LIST
    except IndexError:
        traceback.print_exc()
    except Exception:
        traceback.print_exc()
    
    return wochen_speiseplan


def write_to_document(document_name, data):
    with open(f'data/{document_name}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def write_meal_plan():
    success = False
    start = timer()
    while success == False:
        try:
            print("[+] start scraping")
            json1 = start_scrape_mensa(mensa=True)
            json2 = start_scrape_mensa(rote_beete=True)
            json3 = scrape_qwest()

            write_to_document("mensa1", json1)
            write_to_document("mensa2", json2)
            write_to_document("mensa3", json3)

            print("[+] finished scraping and added to local document")
            success = True
        except Exception:
            traceback.print_exc()
    end = timer()
    print(f'[+] scraping mensa data for all mensas and writing to disk took {end - start} seconds')



def control_job():
    tnow = datetime.datetime.now()
    hh = tnow.strftime('%H')  # hour like '09'
    wk = tnow.isoweekday()  # Mon =1
    print("I'm working %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if (('06' < hh < '22') and (1 <= wk <= 5)):
        write_meal_plan()


schedule.every(10).minutes.do(control_job)

while True:
    schedule.run_pending()
    time.sleep(1)
