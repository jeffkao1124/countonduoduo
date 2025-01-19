from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

import requests
from bs4 import BeautifulSoup
import psycopg2

conn=psycopg2.connect(database=d3oi4f2mbceg54,user=udgq2gm7vpunm4,password=p22b156e475e113aaee82125778740a9c74bcd22f0d0705a8a1fc89502ebfe2f4,host=c9mq4861d16jlm.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com,port=5432)
cur=conn.cursor()

cur.execute('SELECT VERSION()')
results=cur.fetchall()
print ("Database version : %s " % results)

conn.commit()
cur.close()

# from dbModel import *
# from datetime import datetime
# import json
# from sqlalchemy import desc

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('JHhhyAGkeAv1E5c3ylrrPoC1xj5nVbjyxpvFKsenCqcZ43aE1ozhe61IzeVWvHuG8eHehfneXTeNyNVeWig3ThlWoECTzs67Ns6cs4GAINdT4my4BC6xgY88Wn7jAz/cUDpaXEP2FI3y7w7OHYpPVgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('4208ae25a46b2c44a6a1823268d22232')

def get_TodayRate(mode):
    numb= []
    cate=[]
    data=[]
    url_1= "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    resp_1 = requests.get(url_1)
    ms =BeautifulSoup(resp_1.text,"html.parser")

    t1=ms.find_all("td","rate-content-cash text-right print_hide")
    for child in t1:
        numb.append(child.text.strip())

    buy=numb[0:37:2]
    sell=numb[1:38:2]

    t2=ms.find_all("div","hidden-phone print_show")
    for child in t2:
        cate.append(child.text.strip())
    for i in range(19):
        data.append([cate[i] +'買入：'+buy[i]+ '賣出：'+sell[i]])

    if mode==1:
        USD = data[0][0]
        regex = re.compile(r'賣出：(\d+.*\d*)')
        match = regex.search(USD)
        return eval(match.group(1))
    elif mode==2:
        JPY = data[7][0]
        regex = re.compile(r'賣出：(\d+.*\d*)')
        match = regex.search(JPY)
        return eval(match.group(1))
    elif mode==3:
        EUR = data[14][0]
        regex = re.compile(r'賣出：(\d+.*\d*)')
        match = regex.search(EUR)
        return eval(match.group(1))
    else:
        return 1


def get_Boardgame():
    boardgame= []
    url_1= "https://boardgamegeek.com/browse/boardgame"
    resp_1 = requests.get(url_1)
    ms = BeautifulSoup(resp_1.text,"html.parser")

    for i in range(50):
        t1=ms.find_all("div",id="results_objectname"+str(i))
        for bgg in t1:
            boardgame.append(bgg.text.strip())

    return boardgame

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text
    if input_text=='@桌遊':
        output_text = str(get_Boardgame())
        
    elif input_text == '啾啾啾':
        output_text = '啾啾啾'

    elif input_text == '逛夜市' or input_text == '烤小鳥' or input_text == '@吳柏震 ' or input_text == '@林瑋晟 ' or input_text == '@王奕凱 ' or input_text == '@高子承 ' or input_text == '@廖奕翔 ':
        output_text = '不要吃焦阿巴'

    elif input_text == '@廖擊敗':
        output_text = '廖奕翔還錢 操!!'

    elif input_text == 'debug好累':
        output_text = '關我屁事，我已經好幾天沒睡了=='

    elif input_text ==  '乖狗狗':
        line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id=1, sticker_id=2))

    line_bot_api.reply_message(event.reply_token, TextSendMessage (output_text) )


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



# countonduoduo origin version    
# from flask import Flask, request, abort
# from flask_sqlalchemy import SQLAlchemy
# from flask import render_template
# from datetime import datetime
# from sqlalchemy import desc
# from flask import render_template

# app=Flask(__name__)
# app.config[
#     'SQLALCHEMY_DATABASE_URI'] ='postgres://brjgqjmnamwnxc:2038ec5ace178f7e6f34d1015384a39e7274126f60488b14a5403582ae5a8966@ec2-3-95-87-221.compute-1.amazonaws.com:5432/d3s7d1dsfli0sd'

# app.config[
#     'SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# db = SQLAlchemy(app)
# groupId=0
# class usermessage(db.Model):
#     __tablename__ ='usermessage'
#     id = db.Column(db.String(50), primary_key=True)
#     group_num = db.Column(db.Text)
#     nickname = db.Column(db.Text)
#     group_id = db.Column(db.String(50))
#     type = db.Column(db.Text)
#     status = db.Column(db.Text)
#     account = db.Column(db.Text)
#     user_id = db.Column(db.String(50))
#     message = db.Column(db.Text)
#     birth_date = db.Column(db.TIMESTAMP)

# @app.route('/',methods=['POST','GET'])
# def index():
#     group_id=0

#     return render_template('index_form.html',**locals())


# if __name__ =="__main__":
#     app.run()
# ""
