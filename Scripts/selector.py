import json

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

for i in genredict.keys():
    for j in genredict[i]:
        if (j['description'] == None or j['description'].strip() == "" or j['description'] == "unknown"):
            print(f"Found: {j['description']} for description!")
            j['description'] = "No description found."
            
        if (j['genres'] == ["unknown"]):
            print(f"Found: {j['genres']} for genres!")
            j['genres'] = []

        try:
            float(j['rating'])
        except:
            print(f"Found: {j['rating']} for rating!")
            j['rating'] = "0.0"

        try:
            int(j['year'])
        except:
            print(f"Found: {j['year']} for year!")
            j['year'] = "0000"

        try:
            int(j['duration'].split()[0])
        except:
            print(f"Found: {j['duration']} for duration!")
            j['duration'] = "Unknown"

        link = j.pop('links', None)
        j['link'] = None
        try:
            j['link'] = link['1080p']
        except:
            try:
                j['link'] = link['720p']
            except:
                try:
                    j['link'] = link['480p']
                except:
                    try:
                        j['link'] = link['auto']
                    except:
                        pass

with open(r'../Results/filtered.json', 'w') as f:
    f.write(json.dumps(genredict))

print("Done!")