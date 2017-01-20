from flask import Flask, redirect, url_for, request
import json
import requests
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

@app.route('/')
def respond():
   return 'Hello World'

@app.route('/crawl', methods = ['POST','GET'])
def crawl():
    if request.method == 'GET':
        genre = request.args.get('genre')
        return "here is your " + genre

@app.route('/date', methods = ['POST', 'GET'])
def event():
    events = ['다이어리', '밸런타인', '화이트', '블랙','로즈','키스','실버', '그린','포토','와인','무비','허그']
    return "오늘이 인간세계에서는 " + events[0] + "데이라며?"

@app.route('/weather', methods = ['POST','GET'])
def weather():
    if request.method == 'GET':
        longitude = "37.5665350" 
        latitude = "126.9779690"
        url = "http://api.wunderground.com/api/ffbde8a8a4da1bd0/conditions/q/" + longitude +"," + latitude + ".json"
        w = requests.get(url).text
        app.logger.info(w)
        data = json.loads(w)
        data = data['current_observation']
        city = data['display_location']['city'] 
        humidity = data["relative_humidity"]
        temp = str(data["temp_c"])
        return "여기 온도는 무려 " + temp + "도군요! 게다가 습도는 " + humidity +"에요!" 

if __name__ == '__main__':
    handler = RotatingFileHandler('fishy.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True,port=8080,host="0.0.0.0")
