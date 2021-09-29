import json

maindomain = "media.lolisociety.com"
movies = []

with open(r'../Results/nolinks.json', 'r', encoding="utf8") as f:
    movies = json.loads(f.read())

with open(r'../Results/movies.conf', 'a', encoding='utf8') as f:
    for i in movies:
        f.write(f"location /movies/{i[7]}/" + " {\n    proxy_pass " + f"{i[6][:i[6].rfind('/')+1]};" + "\n}\n\n")
        i[6] = f"https://{maindomain}/movies/{i[7]}{i[6][i[6].rfind('/'):]}"

with open(r'../Results/linkspoofed.json', 'w') as f:
    f.write(json.dumps(movies))