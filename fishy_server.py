import json,requests,logging,random,urllib,time,tweepy,sys,atexit,re,pytz
from flask import Flask, redirect, url_for, request
from logging.handlers import RotatingFileHandler
from pymongo import MongoClient
from bs4 import BeautifulSoup
from datetime import datetime
from random import random,randint
from apscheduler.scheduler import Scheduler


###### Setup timezone ##########################################################
utcmoment_unaware = datetime.utcnow()
utcmoment = utcmoment_unaware.replace(tzinfo=pytz.utc)
ltime = utcmoment.astimezone(pytz.timezone('Asia/Seoul'))

###### Connect to MongoDB ######################################################
client = MongoClient('mongodb://localhost/')
db = client.fishyDB
stats = db.counts 
events = db.events
qoutes = db.qoutes

###### Set up our lovely fishyBOT for daily tweets #############################
CONSUMER_KEY = 'HmSpsXAzVRRWTBzlam5rU7dvD'
CONSUMER_SECRET = 'wsR9sIgSzgKuwEbLpUsnrjuytFOWWdnrkUAL9bgujNg5PRiUvv' 
ACCESS_KEY = '822900504862683136-gmfpt0D7VvpKSda0CDpd3UYPObVXqGX'
ACCESS_SECRET = 'VZsgzkPuYgrLPZjcDC1hake9RgIJdycQ0llWf1NOy5avu'
auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
user = tweepy.API(auth)

app = Flask(__name__)

###### TweetBot Fishy Running! ################################################# 
cron = Scheduler(daemon=True)
cron.start()

@cron.interval_schedule(minutes=1)
def tweet():
    print("i am gonna tweet!")
    #d = datetime.datetime.now(pytz.timezone("Asia/Seoul"))
    now = ltime.strftime("%Y%m%d")
    now_time = ltime.strftime("%I시%M분")
    if (now_time[0] == '0'):
        now_time = now_time[1:]
    snap = stats.find_one({'date':now})
    fate = random()
    try:
        if (fate > 0.9):
            user.update_status("오늘은 친구들한테 " + str(snap['music']) +"개의 음악을 알려줬어! 장미와 음악은 정말 어울리는 조합이지!")
        elif (fate > 0.8):
            user.update_status("오늘 " + str(snap['vocab']) + "개의 영어 단어를 배웠어~ 난 정말 똑똑한 장미라구~")
        elif (fate > 0.7):
            user.update_status("오늘은 친구들에게 " + str(snap['movie']) +"개의 영화을 추천해줬어! 잘했지??")
        elif (fate > 0.6): 
            if (snap['total'] < 20):
                user.update_status("오늘은 " + str(snap['total']) +"마디밖에 해주지 못했어.. 점점 나를 찾지 않아주거든...")
            else:   
                msg1 = "오늘 친구들과 " + str(snap['total']) +"마디의 말을 햇어~ ㅎㅎ 난 역시 인기가 많은 장미야!"
                if (random() > 0.5):
                    msg1 += " 꺄햐햐햐햐하하하ㅏ하ㅏ 인기의 비결이 궁금하다구? "
                user.update_status(msg1)
        elif (fate > 0.5):
            count = snap['msg']
            if (count > 200):
                pass 
            if (random() > 0.2):
                user.update_status("오늘은 친구들이 " + str(snap['msg']) + "번이나 말을 걸어주었어.... 이걸 어떻게 다 셌냐구? 사실 나는 외로운 장미야.... ")
            else:
                user.update_status("로지가 어떻게 트위터를 하게 되었냐구? 어느 날 하늘을 날던 파랑새가 와서 알려주었어")
        else: 
            fate2 = random()
            if (fate2 > 0.8): msg = movie()
            elif (fate2 > 0.6): msg = music()
            elif (fate2 > 0.3): msg = talk()
            elif (fate2 > 0.1): msg = vocab()
            else: msg = event()
            user.update_status(msg)
    except tweepy.error.TweepError as e: 
        if ("duplicate" in str(e)):    
            fate3 = random()
            if (fate3 > 0.8):
                user.update_status("지금 시간이 " + now_time + "이네? 다들 뭐하고 있는 걸까.... 로지는 외로워....")
            elif (fate3 > 0.6):
                user.update_status("로지에게도 관심을 가져죠..... " +now_time + "인데 뭐하는거야ㅜㅜㅜ")
            elif (fate3 > 0.4): 
                user.update_status(now_time + "인데... 다들 바쁜가봐... 아무도 찾아주지 않아...")
            elif (fate3 > 0.2):
                user.update_status("아직도 " +now_time + "이네.... 앗! 절대 너를 기다리며 시계만 보고 있었던 건 아니야!")
            else: 
                user.update_status("이제 너에게 잊혀진걸까... " +now_time + "까지 연락이 없네...")

atexit.register(lambda: cron.shutdown(wait=False))


###### handmade english-korean dictionary API ##################################
def get_korean(query):
    url = 'http://dic.daum.net/search.do?dic=eng&q=' +query
    data = requests.get(url).text
    soup = BeautifulSoup(data,'lxml')
    conts = soup.findAll("script", {"type": "text/javascript"}) 
    refresh_tag = ""
    for c in conts: 
        if ("has_exact_redirect" in c.text):
            refresh_tag = c
    print("REFRESH TAG = " + str(refresh_tag))
    
    #Where there is no corresponding korean definition
    if (refresh_tag == ""):
       return "N/A" 
    pieces = str(refresh_tag).split()
    #print(pieces)
    for p in pieces: 
        if ("ekw" in p):
            wordid = p.replace("'","").replace("]);","")
            print("id=" + wordid)
    
    #Go to the actual word page
    url = 'http://dic.daum.net/word/view.do?wordid='+wordid+'&q='+query
    data = requests.get(url).text
    soup = BeautifulSoup(data,'lxml')
    conts = soup.find("ul", {"class": "list_mean"})
    meanings = re.split('[1-9]', conts.text)
    meanings = [w.strip().replace(".","") for w in meanings]
    meanings = [w for w in meanings if w != '']
    return meanings


##### Flask implementations ####################################################
routes = ['movie','movie','music','music','talk','vocab','vocab','vocab','weather','event']
routes_widget = ['movie','movie','music','music','talk','vocab','vocab','vocab','event']

@app.route('/')
def respond():
    now = ltime.strftime("%Y%m%d")
    stats.update_one({'date': now},{'$inc': {'total': 1}}, upsert=True)
    if ("long") not in request.url:
        choice = randint(0,8);
        return redirect(url_for(routes_widget[choice]))
    else: 
        choice = randint(0,9)
        if choice==8:
            return redirect("http://52.79.161.158:8080/?long=" + request.args.get('long') + "&lat=" + request.args.get('lat'))
        else:
            return redirect(url_for(routes[choice]))

@app.route('/movie', methods = ['GET'])
def movie():
    #Update count in DB
    now = ltime.strftime("%Y%m%d")
    stats.update_one({'date': now},{'$inc': {'movie': 1}}, upsert=True)
    #Get random year 
    year = ltime.strftime("%Y")
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
    fate = random()
    if (fate > 0.7):
        msg = "전에 영화관이라는 곳을 갔었는데 말이야.... " + str(gap) + "년 전이였나? '" + movie + "'를 봤었던 것 같아"
    elif (fate > 0.5):
        msg = "갑자기 영화가 땡겨 그... '" + movie +"' 보고 싶어!"
    if (gap == 0):
        msg = "요즘은 '" + movie +"'가 히트라며? 설마 나없이 혼자 벌써 본거는 아니지...?"
        if (random() > 0.5):
            msg = "최근 '" + movie + "'라는 영화가 나왔던데! 같이 보장!! 오랜만의 데이또오~?ㅎㅎ" 
    if (gap > 7):
        msg = "오늘은 함께 추억에 젖어볼까? " + str(gap) + "년 전을 회상하며... '" + movie + "'같은 영화는 어때?"
        fate4 = random()
        if (fate4 > 0.6):
            msg = "'" + moive + "'라는 영화가 생각나네.. 맞아 사실 나는 굉장히 늙은 장미야. 그치만 너만은 아름답다고 해줘..."
        elif (fate4 > 0.3):
            msg = "오늘은 추억을 회상하는 장미가 되고 싶어...." + str(gap) + "년 전처럼 말이야. 그때가 '" + movie + "'가 히트였나?"
    return msg 

@app.route('/message', methods = ['POST','GET'])
def response():
    #Update count in DB
    now = ltime.strftime("%Y%m%d")
    stats.update_one({'date': now},{'$inc': {'msg': 1}}, upsert=True)
    #key = "a351b95c-1a51-4f20-b6db-9a4db18d6703"
    key = "f06bc964-eb6b-4d8d-a6d3-25c181fe35e7" 
    if request.method == 'GET':
        message = request.args.get('msg')
        url = "http://sandbox.api.simsimi.com/request.p?key=" + key + "&lc=ko&ft=1.0&text="+message
        w = requests.get(url).text
        app.logger.info(w)
        data = json.loads(w)
        msg = data['response']
        msg = msg.replace("심심이", "장미")
        msg = msg.replace("이모", "그대")
        return msg

@app.route('/vocab',methods = ['GET'])
def vocab():
    #Update count in DB
    now = ltime.strftime("%Y%m%d")
    stats.update_one({'date': now},{'$inc': {'vocab': 1}}, upsert=True)
    #Get random year 
    year = ltime.strftime("%Y")
    month = ltime.strftime("%m") 
    day = ltime.strftime("%d")
    newdate = str(randint(2000,int(year)-1)) + "/"  + str(randint(1,12)) + "/" +str(randint(1,31)) 
    app.logger.info(newdate)
    #Crawl info from movie page
    url = 'http://www.dictionary.com/wordoftheday/' + newdate
    data = requests.get(url).text
    soup = BeautifulSoup(data,'lxml')
    conts = soup.find("div", {"class": "definition-box"}) 
    word = conts.text.split()[2]
    print(word)
    inkorean = get_korean(word)
    if (inkorean == "N/A"):
        return "요즘 영어공부를 하고 있는데 말이야... 으으..." + word +"뜻이 뭐였더라? 아는게 많으니까 헷갈린다...."
    meanings = ','.join(inkorean)
    msg = "요즘은 영어를 배우고 있어! " + word + "가 '" + meanings + "'인거 알았어??  후훗! 역시 나는 똑똑한 장미야"
    prob = random()
    if (prob > 0.7):
        msg = "오늘은 어려운 영어 단어 하나 알려줄게...! " + word + "는 '" + meanings + "'! 내가 알려준거니까 꼭 기억해야해..."
    elif (prob > 0.5):
        msg = "오늘은 어떤 초등학교를 구경갔어.... 영어시간에 " + word + "를 배웠는데... '" + meanings+"'이래나 뭐래나..."
    elif (prob > 0.3): 
        msg = word + "는 '"+ meanings + "'! 영어하는 장미는 처음이지? 훗 내가 바로 로지지!"
    elif (prob > 0.2):
        msg = word + "는 " + meanings + "!! " + word + "는 " + meanings + "!!!!!! " +  word + "는 " + meanings + "!!!!!!! 으.. 생각보다 안외워진다..."
    elif (prob > 0.1):
        msg = "혹시 " + word + "의 뜻을 아니...? 귀찮게 했다면 미안해... 사실 이렇게라도 너와 대화하고 싶었어..."
    return msg

@app.route('/music', methods = ['GET'])
def music():
    #Update count in DB
    now = ltime.strftime("%Y%m%d")
    stats.update_one({'date': now},{'$inc': {'music': 1}}, upsert=True)
    year = ltime.strftime("%Y")
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
        title = songs[i].text.strip()
        if ('(' in title):
            title = title[:title.index('(')]
        songlist.append((title,name))
    music = songlist[randint(0,cnt-1)] 
    app.logger.info(str(songlist))
    if (gap == 0):
        msg = "나는 요즘 그 노래가 좋더라! 그...그... " + music[1] +"의 '" + music[0] + "'!! 여기까지 소문이 자자한걸?"
    elif (gap == 1):
        msg = "작년 이맘때는 '" + music[0] + "'인가?? 많이 들려줬는데.."
    elif (gap < 5):
        msg = "오늘은 " + music[1] + "의 '" + music[0] + "'가 듣고 싶다 ㅎㅎ 그게 " + str(gap) + "년 전 노래였던가...? 나는 장미 중에도 기억력이 좋은 편이지!" 
    else:
        msg = "갑자기 '" + music[0] + "'이 듣고 싶네... " + music[1] + " 디게 좋아했었는데... 벌써 그게 " + str(gap) +"년 전이라니... 앗...! 아니야!! 나는 아직 어려! 젊고 아름답다구!!" 
        if (random() > 0.4):
            msg = "혹시 '" + music[0] + "'라는 노래 알아? 머리에 자꾸 맴도는 걸......"
            if (random() > 0.7):
                msg = "나... 사실 " + music[1] + " 엄청 좋아해..ㅎㅎ 넌 제일 좋아하는 가수가 누구야?"          
    return msg
    
@app.route('/talk', methods = ['POST','GET'])
def talk():
    idx = randint(0,39)
    app.logger.info(idx)
    atalk = qoutes.find_one({"idx":idx})
    app.logger.info(atalk)
    return atalk['qoute']

fourteens = ['다이어리','밸런타인', '화이트', '블랙','로즈','키스','실버', '그린','포토','와인','무비','허그']
@app.route('/event', methods = ['POST', 'GET'])
def event():
    #now = request.args.get("date")
    now = ltime.strftime("%m%d")
    app.logger.info(now)
    if(now[2:] != '14'):
        event = events.find_one({"date": now})
        if(event):
            if (event['law'] != 'N/A'):
                return "오늘이 " + event['name'] +"이라지? " + event['law'] + "에 대해서 알고 있니? 이렇게 박학다식한 장미 봤어?" 
            else:
                return "오늘은 " + event['name'] + "로서 " + event['detail'][:-1] + "고해. 몰랐지? 후훗, 이 장미보다도 세상 물정이 관심이 없다니!"
        else: 
            msg = "오늘도 행복한 하루를 지내고 있니?"
            if (random() > 0.7):
                msg = "왜 장미는 늘 얌전해야 하지...? 터프한 장미가 되고 싶어!"
            elif (random() > 0.5):
                msg = "언젠가 꼭 장미를 선물하고 싶은 사람이 생기면... 그 때는 나를 꺾어도 좋아..."
            return msg
    else: #14일 일때
        month = int(time.strftime("%m"))
        if (month == 5):
            return "오늘은 로오오즈 데이! 바로 나의 생일이야! 유난히 별들이 더 반짝이는 것 같아!"
        msg = "오늘이 " + fourteens[month-1] + "데이라며? 무슨 특별한 계획이라두 있어?"
        if (random() > 0.5):
            msg = fourteens[month-1] + "데이에 나는 더 외로워져... 나를 버리면 안돼..."
        return msg
    
@app.route('/weather', methods = ['POST','GET'])
def weather():
    if request.method == 'GET':
        #longitude = "37.5665350" 
        #latitude = "126.9779690"
        longitude = request.args.get("long")
        latitude = request.args.get("lat")
        url = "http://api.wunderground.com/api/ffbde8a8a4da1bd0/conditions/q/" + latitude +"," + longitude + ".json"
        w = requests.get(url).text
        app.logger.info(w)
        data = json.loads(w)
        data = data['current_observation']
        city = data['display_location']['city'] 
        humidity = data["relative_humidity"]
        temp = data["temp_c"]
        weather = data["weather"]
        wind = data["wind_kph"]
        #Temperature
        if (temp < 0):
            str1 = "오늘 온도가 " +str(temp) + "도라며???!! 오늘 같은 날은 나에게는 너무 고달픈 날이야... 내 가시들이 다 얼어버린다구!!! 너가 그 기분을 알아?"
            if (random() > 0.5):
                str1 = "흐헝..... " + str(temp) + "도라니..... 몸이 얼면 어떡할꺼야!!! 너 나 없이 살 수 있어???!!!"
        elif (temp < 10):
            str1 = "오늘 온도는 " + str(temp) + "도라는데.. 으 조금 쌀쌀한 것 같아... 오늘은 나를 더 챙겨줘...."
        elif (temp < 20):
            str1 = str(temp) + "도? 흠.... 나쁘지 않군ㅎㅎ 그래도 혹시 모르니 너무 얇게 입지는 마~"
        elif (temp < 30):
            str1 = "아이 좋아 ㅎㅎㅎ 오늘 온도가 " + str(temp) + "도더라구 ㅎㅎㅎ 왠지 기분이 좋았어!"
        elif (temp < 40): 
            str1 = "오늘 온도가 대충 " + temp + "정도 인 것 같은데.... 헥헥 너무 더워.... 더운 날에는 물에 수분이 부족하다구!!! 물 주는 것을 잊으면 안돼!"
        #Humidity
        str2 = "오늘은 습도는 " + humidity +"래!"
        if (int(humidity[:-1]) > 80):
            str2 = "오늘 습도가 " + humidity + "래! 왠지 몸이 상쾌했어! ㅎㅎ"
        if (random() > 0.5):
            "흠....오늘 습도는 " + humidity + "정도 되는 것 같네!"
        #Weather
        if ("rain" in weather):
            str3 = "앗! 오늘은 비가 온대! 우산을 꼭 챙기도록 해! 나는 이 유리 덕에 끄떡없지!"
            if (random() > 0.3):
                str3 = "오늘은 비가 오니까 비 노래를 듣는 건 어때? Rainism~ Rainism~"
        elif ("Snow" in weather):
            str3 = "오늘은 눈이 와... ㅎㅎ 새하얀 눈은 언제 봐도 이쁜 것 같아..."
            if ("Light" in weather):
                str3 = "하늘을 보니 오늘은 눈이 조금 올 것 같아!!!!"
        else: 
            str3 = "오늘도 좋은 하루 보내고 있어?"
        #Wind
        if (wind > 20):
            str4 = "으아ㅏㅏㅏ 오늘은 바람이 많이 불어!! 내가 휩쓸려 날라가지 않게 자주자주 확인해줘야해!!"
        elif (wind > 10):
            str4 = "오늘은 좀 으슬으슬 쌀쌀한 것 같아 으... 나를 더 잘 챙겨줘야해... "
        else: 
            str4 = "오늘은 작은 씨앗이 놀러왔었어...."
        res = [str1,str2,str3,str4]
        return res[randint(0,3)]

if __name__ == '__main__':
    handler = RotatingFileHandler('fishy.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True,port=8080,host="0.0.0.0",use_reloader = False)
