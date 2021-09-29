from os import terminal_size
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import Opera # from selenium.webdriver import Chrome
from selenium.webdriver.opera.options import Options # from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import urllib.request
import traceback
import json
import sys

# For Opera

capabilities = DesiredCapabilities.OPERA # capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"], capabilities["loggingPrefs"] = {"performance": "ALL"}, {"performance": "ALL"}
options = Options()
options.headless = True # Remove this line if you are using chromedriver
options.add_extension(r"..\Resources\AuBlock-Origin_v1.37.2.crx")
driver = Opera(desired_capabilities=capabilities, options=options, executable_path=r"..\Resources\operadriver.exe") # driver = Chrome(desired_capabilities=capabilities, options=options) 
driver.create_options()
mainlink = "https://lookmovie.io"

importantdata = {
    "movienum": 0,
    "exceptions": [],
    "failures": []
}
genredict = {
    "action": [],
    "adventure": [],
    "animation": [],
    "comedy": [],
    "crime": [],
    "drama": [],
    "documentary": [],
    "science-fiction": [],
    "family": [],
    "history": [],
    "fantasy": [],
    "horror": [],
    "music": [],
    "mystery": [],
    "romance": [],
    "thriller": [],
    "war": [],
    "western": []
}
with open(r'../Results/movies.json', 'r') as f:
    file = f.read()
    if len(file) != 0:
        try:
            genredict = json.loads(file)
        except:
            pass

with open(r'../Results/importantdata.json', 'r') as f:
    file = f.read()
    if len(file) != 0:
        try:
            importantdata = json.loads(file)
            importantdata['exceptions'] = []
            importantdata['failures2'] = []
            f.close()
            with open(r'../Results/importantdata.json', 'w') as f:
                f.write(json.dumps(importantdata))
        except:
            pass

class Entry:
    def __init__(self, name, image, description, genres, rating, year, duration, links):
        self.__items = {
            "name": name,
            "image": image,
            "description": description,
            "genres": genres,
            "rating": rating,
            "year": year,
            "duration": duration,
            "links": links
        }

        temp = False
        for i in genres:
            genre = "science-fiction" if i == "sci-fi" else i
            if len(list(filter(lambda x: x["name"] == name, genredict[genre]))) == 0:
                print(f"Adding Entry: {genre} movie - {name}")
                genredict[genre].append(self.__items)
                temp = True
        if temp: 
            print()
        
        if importantdata["movienum"] % 10 == 0:
            with open(r'../Results/movies.json', 'w') as f:
                f.write(json.dumps(genredict))

def dump_to_file(type, data):
    if type == "number":
        importantdata["movienum"] += 1
    if type == "failures":
        importantdata["failures2"].append(data)
    if type == "except":
        importantdata["exceptions"].append(data)
    with open(r'../Results/importantdata.json', 'w') as f:
        f.write(json.dumps(importantdata))

def safe_connect(link, type):
    content = ''
    last = True
    temp = 0
    while last:
        try:
            if type == "UrlLib":
                fp = urllib.request.urlopen(link)
                content = fp.read().decode("utf8")
                fp.close()
            else:
                driver.get(link)
            last = False
        except:
            if temp != 100:
                temp += 1
                print(f"Something went wrong in {type}. Retrying...")
            else:
                print("Too many attempts, failed 100 times. Stopping program... Saving error at importantdata.json for manual analysis.")
                dump_to_file("except", ''.join(traceback.format_exception(*sys.exc_info())))
                dump_to_file("failures", link)
                exit()
    return content

def log_filter(log):
    result = False
    possiblelink = ''
    try:
        possiblelink = log["params"]["headers"][":path"]
        result = log["method"] == "Network.requestWillBeSentExtraInfo" and "/manifests/movies/json/" in possiblelink
    finally:
        return [result, possiblelink]

def get_qualities_html_link(link):
    safe_connect(link, "Selenium")
    html = driver.page_source
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
    validlog = ''
    for i in logs:
        result = log_filter(i)
        if result[0]:
            validlog = result[1]
    return [validlog, html]

# Declaring main processing function
already_counted = []
def processmovie(link):
    if (link not in already_counted):
        try:
            while True:
                importantdata['failures'].remove(link)
        except:
             pass
        already_counted.append(link)
        dump_to_file("number", '')
        print(link)
        temp0 = get_qualities_html_link(link)
        soup = BeautifulSoup(temp0[1], 'html.parser')
        name, image, description, genres, rating, year, duration, links = ['' for i in range(8)]
        try:
            temp = soup.find("h1", {"class": "bd-hd"})
            name = temp.contents[0].strip()

            temp1 = "image"
            try: 
                image = soup.find("p", {"class": "movie__poster lozad"})['data-background-image']
            except:
                image = "unknown"
                print(f"Error on getting {temp1} for {link}!")
            finally:
                pass
            temp1 = "rating"
            try:
                rating = soup.find("div", {"class": "rate"}).find('span').string
            except:
                rating = "unknown"
                print(f"Error on getting {temp1} for {link}!")
            finally:
                pass
            temp1 = "year"
            try:
                year = temp.find("span").string
            except:
                year = "unknown"
                print(f"Error on getting {temp1} for {link}!")
            finally:
                pass
            temp1 = "description"
            try:
                description = soup.find("p", {"class":"description"}).contents[0].strip()
            except:
                description = "unknown"
                print(f"Error on getting {temp1} for {link}!")
            finally:
                pass
            temp1 = "genres"
            try:
                genres = [x.lower() for x in soup.find("div", {"class": "movie-description__header"}).find_all("span")[-1].string.split(", ") if x != '']
            except:
                genres = ["unknown"]
                print(f"Error on getting {temp1} for {link}!")
            finally:
                pass
            temp1 = "duration"
            try:
                duration = soup.find("div", {"class":"movie-description__duration"}).find("span").string
            except:
                duration = "unknown"
                print(f"Error on getting {temp1} for {link}!")
            finally:
                pass

            temp = json.loads(safe_connect(mainlink + temp0[0], "UrlLib"))
            temp['auto'] = mainlink + temp['auto']
            links = temp

            Entry(name, image, description, genres, rating, year, duration, links)
        except:
            print(f"Failure in {link}! {''.join(traceback.format_exception(*sys.exc_info()))}")
            # dump_to_file("except", ''.join(traceback.format_exception(*sys.exc_info())))
            dump_to_file("failures", link)

# Init
[processmovie(failure) for failure in set(importantdata['failures'])]

# Finished!
with open(r'../Results/movies.json', 'w') as f:
    f.write(json.dumps(genredict))
print(f"Done! Total movies scraped is: {importantdata['movienum']}.")