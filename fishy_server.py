from flask import Flask, redirect, url_for, request
import json,requests,logging,random,urllib,time
from logging.handlers import RotatingFileHandler
from pymongo import MongoClient
from bs4 import BeautifulSoup

#Connect to MongoDB
client = MongoClient('mongodb://localhost/')
db = client.fishyDB
oldmovies = db.oldmovies

app = Flask(__name__)

#oldmovies.insert_one({"movie_name": "title!!!"})

@app.route('/')
def respond():
   return 'Hello World'

@app.route('/movie', methods = ['GET'])
def getmovie():
    if request.method  == 'GET':
        #url = 'http://www.melon.com/chart/month/index.htm#params%5Bidx%5D=1&params%5BrankMonth%5D=201012&params%5BisFirstDate%5D=false&params%5BisLastDate%5D=true'
        now = time.strftime("%Y%m%d")
        year = time.strftime("%Y")
        newyr = random.randint(2005,int(year))
        now = str(newyr) + now[4:]
        app.logger.info(now)
        app.logger.info(newyr)
        url = 'http://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&tg=0&date='+now
        data = requests.get(url).text
        soup = BeautifulSoup(data,'lxml')
        conts = soup.find("table", {"summary": "랭킹 테이블"}) 
        top10 = conts.findAll("div", {"class":"tit3"})[:10] #returns a list
        #app.logger.info("top10="+str(top10)+str(len(top10)))
        titles = []
        for i in range(10):
            #app.logger.info(top10[i].text)
            titles.append(top10[i].text)
        movie = titles[random.randint(0,9)][:-1] 
        gap = int(year) - newyr
        msg = "오늘 같은 날 영화는 어때? " + str(gap) + "년 전 이맘 때는 " + movie + "때문에 난리 였었지...." 
        if (random.random() > 0.5):
            msg = "갑자기 영화가 너무 땡기는 걸? " + movie +" 보고 싶어!"
        if (gap == 0):
            msg = "요즘은 " + movie +"가 히트라며? 설마 나없이 혼자 본거는 아니지?"
            if (random.random() > 0.5):
                msg = "최근 " + movie + "라는 영화가 나왔던데! 같이 보장!! ㅎㅎ" 
        if (gap > 7):
            msg = "오늘은 함께 추억에 젖어볼까? " + str(gap) + "년 전을 회상하며..." + movie + "같은 영화는 어때?"
        return msg 

@app.route('/music', methods = ['GET'])
def getmusic():
    if request.method  == 'GET':
        return "music!"

@app.route('/crawl', methods = ['POST','GET'])
def crawl():
    if request.method == 'GET':
        genre = request.args.get('genre')
        return "here is your " + genre

@app.route('/date', methods = ['POST', 'GET'])
def event():
    events = ['다이어리','밸런타인', '화이트', '블랙','로즈','키스','실버', '그린','포토','와인','무비','허그']
    return "오늘이 " + events[0] + "데이라며?"

@app.route('/weather', methods = ['POST','GET'])
def weather():
    if request.method == 'GET':
        #longitude = "37.5665350" 
        #latitude = "126.9779690"
        longitude = request.args.get("long")
        latitude = request.args.get("lat")
        url = "http://api.wunderground.com/api/ffbde8a8a4da1bd0/conditions/q/" + longitude +"," + latitude + ".json"
        w = requests.get(url).text
        #app.logger.info(w)
        data = json.loads(w)
        data = data['current_observation']
        city = data['display_location']['city'] 
        humidity = data["relative_humidity"]
        temp = data["temp_c"]
        if (temp < 0):
            str1 = "오늘 온도가 " +str(temp) + "도라며???!! 오늘 같은 날은 물고기에게는 너무 고달픈 날이야... 물이 다 얼어버린다구!!! 너가 그 기분을 알아?"
            if (random.random() > 0.5):
                str1 = "흐헝..... " + str(temp) + "도라니..... 물이 얼면 어떡할꺼야!!! 너 나 없이 살 수 있어???!!!"
        elif (temp < 10):
            str1 = "오늘 온도는 " + str(temp) + "도라는데.. 으 조금 쌀쌀한 것 같아... 오늘은 나를 더 챙겨줘...."
        elif (temp < 20):
            str1 = str(temp) + "도? 흠.... 나쁘지 않군ㅎㅎ 그래도 혹시 모르니 너무 얇게 입지는 마~"
        elif (temp < 30):
            str1 = "아이 좋아 ㅎㅎㅎ 오늘 온도가 " + str(temp) + "도더라구 ㅎㅎㅎ 왠지 기분이 좋았어!"
        elif (temp < 40): 
            str1 = "오늘 온도가 대충 " + temp + "정도 인 것 같은데.... 헥헥 너무 더워.... 더운 날에는 물에 수분이 부족하다구!!!!"
        res = [str1,"오늘은 습도는 " + humidity +"에요!"]
        return res[random.randint(0,1)]

if __name__ == '__main__':
    handler = RotatingFileHandler('fishy.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True,port=8080,host="0.0.0.0")
