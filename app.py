from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
# Channel Secret
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

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
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


    
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
