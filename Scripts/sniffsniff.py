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
options.add_extension(r"../Resources/AuBlock-Origin_v1.37.2.crx")
driver = Opera(desired_capabilities=capabilities, options=options, executable_path=r"../Resources/operadriver.exe") # driver = Chrome(desired_capabilities=capabilities, options=options) 
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

already_counted = []
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

        for i in genres:
            genre = "science-fiction" if i == "sci-fi" else i
            if len(list(filter(lambda x: x["name"] == name, genredict[genre]))) == 0:
                print(f"Adding Entry: {genre} movie - {name}")
                genredict[genre].append(self.__items)
        print()

        if (name not in already_counted):
            dump_to_file("number", '')
            already_counted.append(name)
        if importantdata["movienum"] % 10 == 0:
            with open(r'../Results/movies.json', 'w') as f:
                f.write(json.dumps(genredict))

def dump_to_file(type, data):
    if type == "number":
        importantdata["movienum"] += 1
    if type == "failures":
        importantdata["failures"].append(data)
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
def find_movies_in_genre_page(html, currentgenre):
    soup = BeautifulSoup(html, 'html.parser')
    for i in soup.find_all("div", {"class": "image__placeholder"}):
        name, image, description, genres, rating, year, duration, links = ['' for i in range(8)]
        try:
            temp = i.find("img")
            name = temp["alt"]

            if len(list(filter(lambda x: x["name"] == name, genredict[currentgenre]))) != 0:
                print(f"Found entry {name}! Skipping...")
                if (name not in already_counted):
                    dump_to_file("number", '')
                    already_counted.append(name)
                continue

            image = temp["data-src"]
            rating = i.find("span").string
            year = i.find("p", {"class": "year"}).string
            temp = get_qualities_html_link(mainlink + i.find("a")["href"])
            nextpage = BeautifulSoup(temp[1], 'html.parser')
            description = nextpage.find("p", {"class":"description"}).contents[0].strip()
            genres = [x.lower() for x in nextpage.find("div", {"class": "movie-description__header"}).find_all("span")[-1].string.split(", ") if x != '']
            duration = nextpage.find("div", {"class":"movie-description__duration"}).find("span").string

            temp = json.loads(safe_connect(mainlink + temp[0], "UrlLib"))
            temp['auto'] = mainlink + temp['auto']
            links = temp

            Entry(name, image, description, genres, rating, year, duration, links)
        except:
            # dump_to_file("except", ''.join(traceback.format_exception(*sys.exc_info())))
            dump_to_file("failures", mainlink + i.find("a")["href"])

# Init

for currentgenre in genredict.keys():
    genreplink = f"{mainlink}/genre/{currentgenre}/page"
    content = safe_connect(f"{genreplink}/1", "UrlLib")
    find_movies_in_genre_page(content, currentgenre)
    for i in range(2, int(BeautifulSoup(content, 'html.parser').find("div", {"class": "pagination__right"}).string.strip().split()[-1]) + 1): 
        find_movies_in_genre_page(safe_connect(f"{genreplink}/{i}", "UrlLib"), currentgenre)

# Finished
with open(r'../Results/movies.json', 'w') as f:
    f.write(json.dumps(genredict))
print(f"Done! Total movies scraped is: {importantdata['movienum']}.")