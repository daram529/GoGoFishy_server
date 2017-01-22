from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests

url = 'https://ko.wikipedia.org/wiki/대한민국의_기념일'
#data = requests.get(url).text
#soup = BeautifulSoup(data,'lxml')
#conts = soup.findAll("table", {"class": "wikitable sortable"})[1] 
#datetop10 = conts.findAll("div", {"class":"tit3"})[:10] #returns a list
#print(conts.text)


#Connect to MongoDB
client = MongoClient('mongodb://localhost/')
db = client.fishyDB
events = db.events 

f = open('events.txt',"r")
f2 = open('events2.txt',"r")

all_event = []

line = f.readline().strip()
while (line): 
    event = []
    event.append(line)
    for i in range(3):
        line = f.readline().strip()
        event.append(line)
    print(event)
    all_event.append(event)
    line = f.readline().strip() 

for e in all_event:
    date = e[1]
    md = date.split()
    md[0] = md[0].replace("월","")
    if (len(md[0]) == 1):
        md[0] = "0" + md[0]
    md[1] = md[1].replace("일","")
    if (len(md[1]) == 1):
        md[1] = "0" + md[1]
    print(md[0]+md[1])
    events.insert_one({"date": md[0]+md[1], "name": e[0], "office": e[2], "law": "N/A","detail": e[3]})

all_event = []

line = f2.readline().strip()
while (line): 
    event = []
    event.append(line)
    for i in range(4):
        line = f2.readline().strip()
        event.append(line)
    print(event)
    all_event.append(event)
    line = f2.readline().strip() 

for e in all_event:
    date = e[1]
    md = date.split()
    md[0] = md[0].replace("월","")
    if (len(md[0]) == 1):
        md[0] = "0" + md[0]
    md[1] = md[1].replace("일","")
    if (len(md[1]) == 1):
        md[1] = "0" + md[1]
    print(md[0]+md[1])
    events.insert_one({"date": md[0]+md[1], "name": e[0], "office": e[2], "law": e[3],"detail": e[4]})


f.close()

