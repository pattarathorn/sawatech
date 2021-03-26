from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from flask import Flask, request, abort
from flask_pymongo import PyMongo
import datetime
import pytz
app = Flask(__name__)
line_bot_api = LineBotApi('MuR72Xn+KcIDblzlw8RI+v9msVbC3f+vpa7wpBjT1rpdvXtWdgz7lvs4g837yrGXsV7/RneVMolyS/tBHR6dN+rh3zGQEM6w4yYcKWzGQvAOyYFyQslivchW5cwu+H5diHT8zaiFIlEqlzMJU86uMgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('df9689715ac16dd5795f9d0c4e4aba57')

app.config['MONGO_URI'] = 'mongodb+srv://sawaembed:212224236@sawatech.1rufs.mongodb.net/embedded'
mongo = PyMongo(app)

collection_userData = mongo.db.user_data
collection_petStatus = mongo.db.pet_status

@app.route('/')
def index():
    return 'Hello World!'

    

@app.route('/GPS', methods=['GET', 'POST'])
def checkgps(**kwargs):
    NamePet = collection_userData.find({"petName":kwargs['nameCat'],"userID":kwargs['userId']})
    print(NamePet[0]["serialID"])
    SerialID = NamePet[0]["serialID"]
    Status = collection_petStatus.find({"serialID":SerialID})
    PetInfo = Status[0]
    print(PetInfo)
    print(type(PetInfo))
    line_bot_api.reply_message(kwargs['replyToken'], TextSendMessage(text = str(PetInfo) ))
        
    #for x in collection_petStatus.find({},{ "petName":kwargs['nameCat']  }):
     #   print(x)
    #if ( collection_petStatus.find({"userID": kwargs['userId']})):
    #    line_bot_api.reply_message(kwargs['replyToken'], TextSendMessage( text = collection_petStatus["temp"] ))

@app.route('/Temperature', methods=['GET', 'POST'])
def Temp(**kwargs):
    return line_bot_api.reply_message(kwargs['replyToken'], TextSendMessage( text = 'อุณหภูมิ @temp องศา' ))

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():

    
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
    return 'Connection'

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #format = "%H:%M:%S"
    #ts = datetime.datetime.now(pytz.timezone('Asia/Bangkok'))
    text = event.message.text
    userId = event.source.user_id
    nameCat = event.message.text
    replyToken = event.reply_token
    
    #if(text == 'time'):
    #    return line_bot_api.reply_message(replyToken,TextSendMessage(text=ts.strftime(format)))
# Rich Menu Switcher
    if text == 'เมนู':
        buttons_template = ButtonsTemplate(
            title='Menu', text='เลือกฟังก์ชัน', actions=[
                URITemplateAction(
                    label='ลงทะเบียนน้องแมว', uri='https://line.me'),
                URITemplateAction(
                    label='แก้ไขข้อมูล', uri='https://line.me')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    else:
        return checkgps(replyToken=replyToken,userId=userId,nameCat=nameCat)
        
    #else:
    #   return line_bot_api.reply_message(replyToken,TextSendMessage(text='ลองคำสั่งอื่น'))

if __name__ == '__main__':
    app.run(debug=True)

