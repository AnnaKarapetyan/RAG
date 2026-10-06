from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from markdownify import markdownify as md
import json

url = "https://fastapi.tiangolo.com/"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    links = map(
        lambda x: urljoin("https://fastapi.tiangolo.com/", x["href"]),
        filter(lambda x: x["href"].startswith(("./tutorial/", "./advanced/")), soup.find_all("a", href=True))
    )
    links = set(links)
    print(len(links))
    names = []
    i = 1
    for link in links:
        print(i)
        i += 1
        response = requests.get(link)
        if response.status_code != 200:
            print("failed:", link, response.status_code)
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.find("article")
        title = soup.find("title").get_text(strip=True)
        for a in article.find_all("a", class_="headerlink"):
            a.decompose()
        text = md(str(article), heading_style="ATX")
        name = link.split("/")[-2]
        if name in names:
            name = f"{name}{i}"
        names.append(name)
        data = {
            "url": link,
            "title": title,
            "text": text
        }
        with open(f"{name}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    print(len(set(names)))
else:
    print('failed:', response.status_code)
with open("response-change-status-code.json", encoding="utf-8") as f:
    data = json.load(f)
print(data["text"])
print (data["url"])

