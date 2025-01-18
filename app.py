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
from dbModel import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('JHhhyAGkeAv1E5c3ylrrPoC1xj5nVbjyxpvFKsenCqcZ43aE1ozhe61IzeVWvHuG8eHehfneXTeNyNVeWig3ThlWoECTzs67Ns6cs4GAINdT4my4BC6xgY88Wn7jAz/cUDpaXEP2FI3y7w7OHYpPVgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('4208ae25a46b2c44a6a1823268d22232')

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
# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     message = TextSendMessage(text=event.message.text)
#     line_bot_api.reply_message(event.reply_token, message)

def get_history_list():   #取得最新資料
    data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).limit(1).all()
    history_dic = {}
    history_list = []    
    for _data in data_UserData:
        history_dic['Status'] = _data.status
        history_dic['type'] = _data.type
        history_dic['user_id'] = _data.user_id
        history_dic['group_id'] = _data.group_id
        history_list.append(history_dic)
    return history_list

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text
    history_list = get_history_list()
    if history_list[0]['type'] == 'user':      #個人部分
        selfId = history_list[0]['user_id']
        if (history_list[0]['Status'] == 'save') and ('記帳' in input_text):
            output_text='記帳成功'
        elif input_text == '@官網':
            output_text = 'https://reurl.cc/4yjNyY'
        elif input_text =='@help':
            output_text='請直接把多多分帳邀請至群組以解鎖分帳功能唷~'

        elif '多多公布欄' in input_text:
            output_text='多多感謝您的體諒！我會在群組中繼續為大家服務。'
        elif input_text =='理財':            
            line_bot_api.reply_message(  
            event.reply_token,
            TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='理財小幫手',
                    text='請選擇功能',
                    actions=[
                        URITemplateAction(
                            label='股市',
                            uri='https://tw.stock.yahoo.com/'
                        ),
                        URITemplateAction(
                            label='匯率',
                            uri='https://rate.bot.com.tw/xrt?Lang=zh-TW'
                        ),
                        URITemplateAction(
                            label='財經新聞',
                            uri='https://www.msn.com/zh-tw/money'
                        )
                        ]
                    )
                )
            )

    elif history_list[0]['type'] == 'room':  #聊天室部分
        Carousel_template = TemplateSendMessage(
                            alt_text='請把我加入群組',
                            template=ImageCarouselTemplate(
                            columns=[
            ImageCarouselColumn(
                image_url="https://i.imgur.com/wUob12p.jpg",
                action=URITemplateAction(
                    uri="https://i.imgur.com/wUob12p.jpg"
                )
            ),
            ImageCarouselColumn(
                image_url="https://i.imgur.com/MRMWivy.jpg",
                action=URITemplateAction(
                    uri="https://i.imgur.com/MRMWivy.jpg"
                )
            )
        ]     
                        )
                    )
        line_bot_api.reply_message(event.reply_token,Carousel_template)    

    else:  #群組部分
        selfGroupId = history_list[0]['group_id']
        if (history_list[0]['Status'] == 'set') and ('@分帳設定' in input_text):
            groupNumber=get_groupPeople(history_list,1)
            output_text='分帳設定成功:共有'+str(groupNumber)+'人分帳'

        elif (history_list[0]['Status'] == 'save') and ('@分帳' in input_text):
            output_text='分帳記錄成功'

        elif (history_list[0]['Status'] == 'None') and ('@分帳' in input_text):
            output_text='分帳記錄失敗'

        elif input_text == '@設定查詢':
            groupMember=get_groupPeople(history_list,2)
            output_text="分帳名單："
            for i in range(get_groupPeople(history_list,1)):
                output_text+='\n'+groupMember[i]

        elif '@美金設定' in input_text:
            NowRate=get_TodayRate(1)
            output_text="今日匯率："+str(NowRate)

        elif '@日圓設定' in input_text:
            NowRate=get_TodayRate(2)
            output_text="今日匯率："+str(NowRate)
        
        elif '@歐元設定' in input_text:
            NowRate=get_TodayRate(3)
            output_text="今日匯率："+str(NowRate)

        elif input_text == '@刪除':
            for i in range(3):
                data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='save').delete(synchronize_session='fetch')
            output_text='刪除成功'
            db.session.commit()

        elif input_text == '@設定刪除':
            data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='set').delete(synchronize_session='fetch')
            db.session.commit()
            output_text='刪除成功'
        
        elif '@clear' in input_text:  #刪除單個分帳者
            data_UserData = usermessage.query.filter(usermessage.status=='set').filter(usermessage.group_id==selfGroupId)
            del_spiltperson = ' '+input_text.replace('@clear','').strip(' ') +' '
            for _data in data_UserData:
                old_nickname = ' '+_data.nickname+' '
                old_nickname = old_nickname
                if old_nickname.count(del_spiltperson):
                    new_nickname = old_nickname.replace(del_spiltperson,' ').replace('  ',' ').strip(' ')
                    add_data = usermessage( 
                    id = _data.id, 
                    group_num = '0', 
                    nickname = new_nickname,
                    group_id = _data.group_id, 
                    type = _data.type, 
                    status = 'set', 
                    account = '0', 
                    user_id = _data.user_id, 
                    message = _data.message, 
                    birth_date = _data.birth_date
                    )
                    personID = _data.id
                    data_UserData = usermessage.query.filter(usermessage.id==personID).delete(synchronize_session='fetch')
                    db.session.add(add_data)
                    db.session.commit()
                    output_text="刪除成功，若被刪除的人在帳目中，請記得把帳目也修改掉!\n\n分帳名單:"
            try:
                if output_text=='刪除成功，若被刪除的人在帳目中，請記得把帳目也修改掉!\n\n分帳名單:':
                    groupMember=get_groupPeople(history_list,2)
                    for i in range(get_groupPeople(history_list,1)):
                        output_text+='\n'+groupMember[i]
            except: 
                output_text = '刪除失敗'

        
        elif '@delete' in input_text: #刪除單筆分帳
            count = usermessage.query.filter(usermessage.status=='save').filter(usermessage.group_id==selfGroupId).count()
            try:
                del_number = int (input_text.strip('@delete '))
                if del_number <= count :
                    data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.status=='save').filter(usermessage.group_id==selfGroupId)[del_number-1:del_number]
                    for _data in data_UserData:
                        personID = _data.id
                    data_UserData = usermessage.query.filter(usermessage.id==personID).delete(synchronize_session='fetch')
                    output_text='刪除成功'+'\n\n'+'記帳清單：'+'\n'+get_settleList(selfGroupId)
                    db.session.commit()
                else:
                    output_text='刪除失敗'
            except:
                output_text='刪除失敗'

        

        elif input_text == '@查帳':
            output_text = get_settleList(selfGroupId)
            flexmsg ={
  "type": "flex",
  "altText": "Flex Message",
  "contents": {
    "type": "bubble",
    "hero": {
      "type": "image",
      "url": "https://imgur.com/KahFQi9.jpg",
      "size": "full",
      "aspectRatio": "20:13",
      "aspectMode": "cover",
      "action": {
        "type": "text",
        "text":"查查"
      }
    },
    "body": {
      "type": "box",
      "layout": "vertical",
      "contents": [
        {
          "type": "text",
          "text": "查帳",
          "size": "xl",
          "weight": "bold"
        },
        {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "margin": "lg",
          "contents": [
            {
              "type": "box",
              "layout": "baseline",
              "spacing": "sm",
              "contents": [
                {
                  "type": "text",
                  "text": output_text+". . .",
                  "flex": 5,
                  "size": "sm",
                  "color": "#666666",
                  "wrap": True
                }
              ]
            },
          ]
        }
      ]
    },
    "footer": {
      "type": "box",
      "layout": "vertical",
      "flex": 0,
      "spacing": "sm",
      "contents": [
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": "查看更多",
            "uri": "https://liff.line.me/1654876504-rK3v07Pk"
          },
          "height": "sm",
          "style": "link"
        },
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": "記錄分帳",
            "uri": "https://liff.line.me/1654876504-9wWzOva7"
          },
          "height": "sm",
          "style": "link"
        },
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": "編輯分帳者",
            "uri": "https://liff.line.me/1654876504-QNXjnrl2"
          },
          "height": "sm",
          "style": "link"
        },
        {
          "type": "spacer",
          "size": "sm"
        }
      ]
    }
  }
}
            line_bot_api.reply_message(event.reply_token,messages=FlexSendMessage.new_from_json_dict(flexmsg))

        elif input_text =='@結算':            
            selfGroupId = history_list[0]['group_id']
            dataSettle_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId ).filter(usermessage.status=='save').filter(usermessage.type=='group')
            historySettle_list = []
            person_list  = get_groupPeople(history_list,2)
            person_num = get_groupPeople(history_list,1)
            for _data in dataSettle_UserData:
                historySettle_dic = {}
                historySettle_dic['Account'] = _data.account
                historySettle_dic['GroupPeople'] =_data.group_num
                historySettle_dic['message'] = _data.message
                historySettle_list.append(historySettle_dic)
            
            dataNumber=len(historySettle_list)
            account = np.zeros(person_num)
            exchange_rate_USD = 0
            exchange_rate_JPY = 0
            exchange_rate_EUR = 0
            for i in range(dataNumber):   #分帳金額
                b=dict(historySettle_list[i])
                GroupPeopleString=b['GroupPeople'].strip(' ').split(' ')  #刪除代墊者
                del GroupPeopleString[0]
                
                if 'USD' in b['message']:   #匯率轉換
                    if exchange_rate_USD:
                        exchange_rate = exchange_rate_USD
                    else:
                        exchange_rate_USD = get_exchangeRate(1)
                        exchange_rate = exchange_rate_USD
                elif 'JPY' in b['message']:
                    if exchange_rate_JPY:
                        exchange_rate = exchange_rate_JPY
                    else:
                        exchange_rate_JPY = get_exchangeRate(2)
                        exchange_rate = exchange_rate_JPY
                elif 'EUR' in b['message']:
                    if exchange_rate_EUR:
                        exchange_rate = exchange_rate_EUR
                    else:
                        exchange_rate_EUR = get_exchangeRate(3)
                        exchange_rate = exchange_rate_EUR
                else:
                    exchange_rate = 1

                payAmount = exchange_rate*int(b['Account']) / len(GroupPeopleString)
                a1=set(person_list)      #分帳設定有的人
                a2=set(GroupPeopleString)
                duplicate = list(a1.intersection(a2))       #a1和a2重複的人名
                for j in range(len(duplicate)):      #分帳金額
                    place=person_list.index(duplicate[j])
                    payAmount_place = GroupPeopleString.index(duplicate[j]) +1  #多種分帳金額 - 金額位置 
                    if ( payAmount_place < len(GroupPeopleString) and GroupPeopleString[payAmount_place].isdigit() ): 
                        payAmount = exchange_rate*int(GroupPeopleString[payAmount_place])                   
                    account[place] -= payAmount
                    
            for j in range(dataNumber):  #代墊金額
                b=dict(historySettle_list[j])
                GroupPeopleString=b['GroupPeople'].strip(' ').split(' ')
                if 'USD' in b['message']:   #匯率轉換
                    if exchange_rate_USD:
                        exchange_rate = exchange_rate_USD
                    else:
                        exchange_rate_USD = get_exchangeRate(1)
                        exchange_rate = exchange_rate_USD
                elif 'JPY' in b['message']:
                    if exchange_rate_JPY:
                        exchange_rate = exchange_rate_JPY
                    else:
                        exchange_rate_JPY = get_exchangeRate(2)
                        exchange_rate = exchange_rate_JPY
                elif 'EUR' in b['message']:
                    if exchange_rate_EUR:
                        exchange_rate = exchange_rate_EUR
                    else:
                        exchange_rate_EUR = get_exchangeRate(3)
                        exchange_rate = exchange_rate_EUR
                else:
                    exchange_rate = 1

                for i in range(person_num):  
                    if GroupPeopleString[0] ==  person_list[i]:
                        account[i] += exchange_rate * int(b['Account'])

            #將人和錢結合成tuple，存到一個空串列
            person_account=[]
            for i in range(person_num):
                zip_tuple=(person_list[i],account[i])
                person_account.append(zip_tuple)

            #重複執行交換動作
            result=""
            for i in range(person_num-1):  #排序
                person_account=sorted(person_account, key = lambda s:s[1])

                #找到最大、最小值
                min_tuple=person_account[0]
                max_tuple=person_account[-1]

                #找到目前代墊最多的人
                if i==0:
                    maxPerson=max_tuple[0]
                    minPerson=min_tuple[0]

                
                min=float(min_tuple[1])
                max=float(max_tuple[1])

                #交換，印出該付的錢
                if min==0 or max==0:
                    pass
                elif (min+max)>0:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+" "+str(abs(round(min,2)))+'元'+'\n'
                    max_tuple=(max_tuple[0],min+max)
                    min_tuple=(min_tuple[0],0)
                elif (min+max)<0:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+" "+str(abs(round(max,2)))+'元'+'\n'
                    min_tuple=(min_tuple[0],min+max)
                    max_tuple=(max_tuple[0],0)
                else:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+" "+str(abs(round(max,2)))+'元'+'\n'
                    min_tuple=(min_tuple[0],0)
                    max_tuple=(max_tuple[0],0)
                
                person_account[0]=min_tuple
                person_account[-1]=max_tuple
            # result=result+'\n'+'下次不要再讓'+str(max_tuple[0])+'付錢啦! TA幫你們付很多了!'

            output_text = result.strip('\n')
            
            flexmsg ={
                    "type": "flex",
                    "altText": "Flex Message",
                    "contents": {
                        "type": "bubble",
                        "hero": {
                        "type": "image",
                        "url": "https://imgur.com/GteXIvk.jpg",
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "action": {
                            "type": "text",
                            "text":"借錢要還，誰還要借?"
                        }
                        },
                        "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                            "type": "text",
                            "text": "簡化版本",
                            "size": "xl",
                            "weight": "bold"
                            },
                            {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                    "type": "text",
                                    "text": result+". . .",
                                    "flex": 5,
                                    "size": "sm",
                                    "color": "#666666",
                                    "wrap": True
                                    }
                                ]
                                },
                            ]
                            }
                        ]
                        },
                        "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 0,
                        "spacing": "sm",
                        "contents": [
                            {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "查看更多",
                                "uri": "https://liff.line.me/1654876504-rK3v07Pk"
                            },
                            "height": "sm",
                            "style": "link"
                            },
                            {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "記錄分帳",
                                "uri": "https://liff.line.me/1654876504-9wWzOva7"
                            },
                            "height": "sm",
                            "style": "link"
                            },
                            {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "編輯分帳者",
                                "uri": "https://liff.line.me/1654876504-QNXjnrl2"
                            },
                            "height": "sm",
                            "style": "link"
                            },
                            {
                            "type": "spacer",
                            "size": "sm"
                            }
                        ]
                        }
                    }
                    }
            line_bot_api.reply_message(event.reply_token,messages=FlexSendMessage.new_from_json_dict(flexmsg))

        elif input_text =='@稍微':             
            selfGroupId = history_list[0]['group_id'] 
            dataSettle_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId ).filter(usermessage.status=='save').filter(usermessage.type=='group') 
            historySettle_list = [] 
            person_list  = get_groupPeople(history_list,2)  #分帳設定人名
            person_num = get_groupPeople(history_list,1)  #分帳設定人數
            for _data in dataSettle_UserData: 
                historySettle_dic = {} 
                historySettle_dic['Account'] = _data.account 
                historySettle_dic['GroupPeople'] =_data.group_num 
                historySettle_dic['message'] = _data.message
                historySettle_list.append(historySettle_dic) 
                
            dataNumber=len(historySettle_list) 
            account= np.zeros((person_num,person_num)) 
            exchange_rate_USD = 0
            exchange_rate_JPY = 0
            exchange_rate_EUR = 0
            for i in range(dataNumber): 
                b=dict(historySettle_list[i]) 
                GroupPeopleString=b['GroupPeople'].split(' ')

                if 'USD' in b['message']:   #匯率轉換
                    if exchange_rate_USD:
                        exchange_rate = exchange_rate_USD
                    else:
                        exchange_rate_USD = get_exchangeRate(1)
                        exchange_rate = exchange_rate_USD
                elif 'JPY' in b['message']:
                    if exchange_rate_JPY:
                        exchange_rate = exchange_rate_JPY
                    else:
                        exchange_rate_JPY = get_exchangeRate(2)
                        exchange_rate = exchange_rate_JPY
                elif 'EUR' in b['message']:
                    if exchange_rate_EUR:
                        exchange_rate = exchange_rate_EUR
                    else:
                        exchange_rate_EUR = get_exchangeRate(3)
                        exchange_rate = exchange_rate_EUR
                else:
                    exchange_rate = 1
                payAmount = exchange_rate*int(b['Account']) / (len(GroupPeopleString)-1)  #不包含代墊者
                a1=set(person_list)      #分帳設定有的人 
                a2=set(GroupPeopleString) 
                duplicate = list(a1.intersection(a2))         #a1和a2重複的人名 

                for j in range(len(duplicate)):      #誰付誰錢矩陣 2給1 
                    place1=person_list.index(GroupPeopleString[0]) 
                    place2=person_list.index(duplicate[j]) 
                    account[place1][place2]+=payAmount 
            result=""
            for j in range ( person_num ): #誰付誰錢輸出 
                for i in range ( person_num ): 
                   payAmount = account[i][j] - account[j][i]
                   if ( payAmount>0 ): 
                        result += person_list[j]+'付給'+person_list[i] +" "+ str(round(payAmount,2)) +'元'+'\n' 
            output_text = result.strip('\n')
     
        elif input_text == '@清空資料庫':
            data_UserData = usermessage.query.filter(usermessage.status=='None').delete(synchronize_session='fetch')
            db.session.commit()
            output_text = '爽啦沒資料囉\n快給我重新設定匯率'
        
        elif '@查查廖擊敗'  in input_text:
            output_text = "欠錢不還啦 幹你娘"

        elif input_text =='@多多':
            try:
                message =TextSendMessage(
                    text="快速選擇下列功能：",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(label="主選單",text="@選單")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="查帳",text="@查帳")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="簡化結算",text="@結算")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="不簡化結算",text="@稍微")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="使用說明",text="@help")
                            ),
                        ]

                    )
                    )
                line_bot_api.reply_message(event.reply_token,message)
            except:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage ('發生錯誤!'))

        elif input_text =='@help' :
            Carousel_template = TemplateSendMessage(
                            alt_text='使用說明',
                            template=ImageCarouselTemplate(
                            columns=[
                ImageCarouselColumn(
                    image_url="https://imgur.com/xvZq2mD.png",
                    action=URITemplateAction(
                        uri="https://imgur.com/xvZq2mD.png"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://imgur.com/oER72MY.png",
                    action=URITemplateAction(
                        uri="https://imgur.com/oER72MY.png"
                    )
                )
            ]     
                            )
                        )
            line_bot_api.reply_message(event.reply_token,Carousel_template)


            line_bot_api.reply_message(event.reply_token,flexmsg)
        elif input_text =='@選單'  :
            message = ImagemapSendMessage(
                            base_url="https://imgur.com/cODeL32.jpg",
                            alt_text='功能總覽',
                            base_size=BaseSize(height=927, width=1040),
                            actions=[
            URIImagemapAction(
                #分帳者設定
                link_uri="https://liff.line.me/1654876504-QNXjnrl2",
                area=ImagemapArea(
                    x=0, y=464, width=522, height=459
                )
            ),
            URIImagemapAction(
                #記錄分帳
                link_uri="https://liff.line.me/1654876504-9wWzOva7",
                area=ImagemapArea(
                    x=0, y=0, width=521, height=463
                )
            ),
            MessageImagemapAction(
                #使用說明
                text="@help",
                area=ImagemapArea(
                    x=525, y=464, width=515, height=459
                )
            ),
            URIImagemapAction(
                #查帳結算
                link_uri="https://liff.line.me/1654876504-rK3v07Pk",
                area=ImagemapArea(
                    x=522, y=0, width=518, height=463
                )
            )
        ]
                       
                            )
            line_bot_api.reply_message(event.reply_token,message)
        
        
        elif input_text== '@官網':
            output_text = 'https://reurl.cc/4yjNyY'

        elif input_text=='@桌遊':
            output_text = str(get_Boardgame())

        elif input_text=='@電影':
            output_text = str(get_movie())

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
