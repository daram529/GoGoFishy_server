from flask import Flask, redirect, url_for, request
import json,requests,logging,random,urllib,time
from logging.handlers import RotatingFileHandler
from pymongo import MongoClient
from bs4 import BeautifulSoup
from random import random,randint
import tweepy,time,sys
import atexit
from apscheduler.scheduler import Scheduler

#Connect to MongoDB
client = MongoClient('mongodb://localhost/')
db = client.fishyDB
stats = db.counts 

#Set up our lovely fishyBOT for daily tweets
CONSUMER_KEY = 'HmSpsXAzVRRWTBzlam5rU7dvD'
CONSUMER_SECRET = 'wsR9sIgSzgKuwEbLpUsnrjuytFOWWdnrkUAL9bgujNg5PRiUvv' 
ACCESS_KEY = '822900504862683136-gmfpt0D7VvpKSda0CDpd3UYPObVXqGX'
ACCESS_SECRET = 'VZsgzkPuYgrLPZjcDC1hake9RgIJdycQ0llWf1NOy5avu'
auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
user = tweepy.API(auth)

#exec(open("./tweetbot.py").read())
#oldmovies.insert_one({"movie_name": "title!!!"})

app = Flask(__name__)

cron = Scheduler(daemon=True)
cron.start()

@cron.interval_schedule(minutes=1)
def tweet():
    print("i am gonna tweet!")
    #d = datetime.datetime.now(pytz.timezone("Asia/Seoul"))
    now = time.strftime("%Y%m%d")
    now_time = time.strftime("%I시%M분")
    if (now_time[0] == '0'):
        now_time = now_time[1:]
    snap = stats.find_one({'date':now})
    fate = random()
    try:
        if (fate < 0.5):
            user.update_status("오늘은 친구들한테 " + str(snap['music']) +"개의 음악을 추천해줬어! 헤헷!!")
        else:
            user.update_status("오늘은 친구들에게 " + str(snap['movie']) +"개의 영화을 추천해줬어! 잘했지??")
    except tweepy.error.TweepError as e: 
        if ("duplicate" in str(e)):    
            try: 
                user.update_status("심심해 심심해!! 놀아줘!!! 나랑 놀아줘!!!!")
            except tweepy.error.TweepError as e: 
                if ("duplicate" in str(e)):    
                    user.update_status("어머! 벌써 " + now_time + "이네! 친구랑 놀다보니까 시간가는 줄도 몰랐다구~")

atexit.register(lambda: cron.shutdown(wait=False))


@app.route('/')
def respond():
    fate = random()
    if (fate < 0.5):
        return redirect(url_for('movie'))
    else:
        return redirect(url_for('music'))

@app.route('/movie', methods = ['GET'])
def movie():
    if request.method  == 'GET':
        #Update count in DB
        now = time.strftime("%Y%m%d")
        stats.update_one({'date': now},{'$inc': {'movie': 1}}, upsert=True)
        #Get random year 
        year = time.strftime("%Y")
        newyr = randint(2005,int(year))
        now = str(newyr) + now[4:]
        app.logger.info(now)
        app.logger.info(newyr)
        #Crawl info from movie page
        url = 'http://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&tg=0&date='+now
        data = requests.get(url).text
        soup = BeautifulSoup(data,'lxml')
        conts = soup.find("table", {"summary": "랭킹 테이블"}) 
        top10 = conts.findAll("div", {"class":"tit3"})[:10] #returns a list
        #app.logger.info("top10="+str(top10)+str(len(top10)))
        titles = []
        for i in range(10):
            #app.logger.info(top10[i].text)
            titles.append(top10[i].text.strip())
        movie = titles[randint(0,9)] 
        gap = int(year) - newyr
        msg = "오늘 같은 날 영화는 어때? " + str(gap) + "년 전 이맘 때는 '" + movie + "'때문에 난리 였었지...." 
        if (random() > 0.5):
            msg = "갑자기 영화가 너무 땡기는 걸? '" + movie +"' 보고 싶어!"
        if (gap == 0):
            msg = "요즘은 '" + movie +"'가 히트라며? 설마 나없이 혼자 본거는 아니지?"
            if (random() > 0.5):
                msg = "최근 '" + movie + "'라는 영화가 나왔던데! 같이 보장!! ㅎㅎ" 
        if (gap > 7):
            msg = "오늘은 함께 추억에 젖어볼까? " + str(gap) + "년 전을 회상하며... '" + movie + "'같은 영화는 어때?"
        return msg 

@app.route('/music', methods = ['GET'])
def music():
    if request.method  == 'GET':
        #Update count in DB
        now = time.strftime("%Y%m%d")
        stats.update_one({'date': now},{'$inc': {'music': 1}}, upsert=True)
        year = time.strftime("%Y")
        newyr = int(year)
        if (random() > 0.3):
            newyr = randint(2004,int(year))
        now = str(newyr) + now[4:]
        gap = int(year) - newyr
        app.logger.info(newyr)
        url = 'http://music.bugs.co.kr/chart/track/day/total?chartdate='+now
        app.logger.info(url)
        data = requests.get(url).text
        soup = BeautifulSoup(data,'lxml')
        conts = soup.find("table", {"class": "list trackList byChart"}) 
        cnt = 5
        if (gap == 0):
            cnt = 15 
        songs = conts.findAll("p", {"class":"title"})[:cnt] #returns a list
        artists = conts.findAll("p", {"class":"artist"})[:cnt] #returns a list
        #app.logger.info(songs)
        #app.logger.info(artists)
        songlist = []
        for i in range(cnt):
            more = artists[i].find("a",{"class":"more"})
            if (more):
                more.decompose()
            name = artists[i].text.strip()
            if ('(' in name):
                name = name[:name.index('(')]
            songlist.append((songs[i].text.strip(),name))
        music = songlist[randint(0,cnt-1)] 
        app.logger.info(str(songlist))
        if (gap == 0):
            msg = "나는 요즘 그 노래가 좋더라! 그...그... " + music[1] +"의 '" + music[0] + "'!! 바다 속까지 소문이 자자하다구~"
        elif (gap == 1):
            msg = "작년 이맘때는 '" + music[0] + "'인가?? 많이 들려줬는데.. 다시 듣자!!!"
        elif (gap < 5):
            msg = "오늘은 " + music[1] + "의 '" + music[0] + "'가 듣고 싶다 ㅎㅎ 그게 " + str(gap) + "년 전 노래였던가...? 물고기라고 기억이 다 안좋은거는 아니야!!!" 
        else:
            msg = "갑자기 '" + music[0] + "'이 듣고 싶네... " + music[1] + " 디게 좋아했었는데... 벌써 그게 " + str(gap) +"년 전이라니... 앗...! 아니야!! 물론 엄마가 알려준거야! 나는 사실 굉장히 어리다구!!" 
            if (random() > 0.4):
                msg = "혹시 '" + music[0] + "'라는 노래 알아? 내 친구가 바다 속에 자꾸 흥얼거리길래...."
                if (random() > 0.7):
                    msg = "나... 사실 " + music[1] + " 엄청 좋아해!!! ㅎㅎ 넌 제일 좋아하는 가수가 누구야?"          
        return msg

@app.route('/message', methods = ['POST','GET'])
def response():
    key = "a351b95c-1a51-4f20-b6db-9a4db18d6703"
    if request.method == 'GET':
        message = request.args.get('msg')
        url = "http://sandbox.api.simsimi.com/request.p?key=" + key + "&lc=ko&ft=1.0&text="+message
        w = requests.get(url).text
        app.logger.info(w)
        data = json.loads(w)
        msg = data['response']
        return msg

@app.route('/location', methods = ['POST','GET'])
def location():
    if request.method == 'GET':
        genre = request.args.get('genre')
        return "here is your " + genre

@app.route('/event', methods = ['POST', 'GET'])
def event():
    events = ['다이어리','밸런타인', '화이트', '블랙','로즈','키스','실버', '그린','포토','와인','무비','허그']
    return "오늘이 " + events[0] + "데이라며?"

@app.route('/weather', methods = ['POST','GET'])
def weather():
    if request.method == 'GET':
        longitude = "37.5665350" 
        latitude = "126.9779690"
        #longitude = request.args.get("long")
        #latitude = request.args.get("lat")
        url = "http://api.wunderground.com/api/ffbde8a8a4da1bd0/conditions/q/" + longitude +"," + latitude + ".json"
        w = requests.get(url).text
        app.logger.info(w)
        data = json.loads(w)
        data = data['current_observation']
        city = data['display_location']['city'] 
        humidity = data["relative_humidity"]
        temp = data["temp_c"]
        weather = data["weather"]
        #Temperature
        if (temp < 0):
            str1 = "오늘 온도가 " +str(temp) + "도라며???!! 오늘 같은 날은 물고기에게는 너무 고달픈 날이야... 물이 다 얼어버린다구!!! 너가 그 기분을 알아?"
            if (random() > 0.5):
                str1 = "흐헝..... " + str(temp) + "도라니..... 물이 얼면 어떡할꺼야!!! 너 나 없이 살 수 있어???!!!"
        elif (temp < 10):
            str1 = "오늘 온도는 " + str(temp) + "도라는데.. 으 조금 쌀쌀한 것 같아... 오늘은 나를 더 챙겨줘...."
        elif (temp < 20):
            str1 = str(temp) + "도? 흠.... 나쁘지 않군ㅎㅎ 그래도 혹시 모르니 너무 얇게 입지는 마~"
        elif (temp < 30):
            str1 = "아이 좋아 ㅎㅎㅎ 오늘 온도가 " + str(temp) + "도더라구 ㅎㅎㅎ 왠지 기분이 좋았어!"
        elif (temp < 40): 
            str1 = "오늘 온도가 대충 " + temp + "정도 인 것 같은데.... 헥헥 너무 더워.... 더운 날에는 물에 수분이 부족하다구!!!!"
        #Humidity
        str2 = "오늘은 습도는 " + humidity +"래!"
        if (int(humidity[:-1]) > 80):
            str2 = "오늘 습도가 " + humidity + "래! 왠지 몸이 상쾌했어! ㅎㅎ"
        if (random() > 0.5):
            "흠....오늘 습도는 " + humidity + "정도 되는 것 같네!"
        #Weather
        if ("rain" in weather):
            str3 = "앗! 오늘은 비가 온대! 우산을 꼭 챙기도록 해!"
            if (random() > 0.3):
                str3 = "오늘은 비가 오니까 비 노래를 듣는 건 어때? Rainism~ Rainism~"
        elif ("Snow" in weather):
            str3 = "오늘은 눈이 와... ㅎㅎ 새하얀 눈은 언제 봐도 이쁜 것 같아..."
            if ("Light" in weather):
                str3 = "하늘을 보니 오늘은 눈이 조금 올 것 같아! 물고기도 하늘을 볼 수 있다구!"
        else: 
            str3 = "오늘도 좋은 하루 보내~"
        res = [str1,str2,str3]
        return res[randint(0,2)]

if __name__ == '__main__':
    handler = RotatingFileHandler('fishy.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True,port=8080,host="0.0.0.0",use_reloader = False)
