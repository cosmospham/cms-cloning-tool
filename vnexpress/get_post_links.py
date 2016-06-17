import urllib
from bs4 import BeautifulSoup
import codecs

string = ""  
content = urllib.urlopen("http://vnexpress.net/").read()
soup = BeautifulSoup(content)
title_news = soup.select(".title_news a.txt_link")

for title in title_news:
    link = title['href']

    f = codecs.open("links.txt", "a", "utf-8")
    f.write(link + "\n")
    f.close()