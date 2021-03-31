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
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    session,
    make_response,
    redirect,
    flash,
    Markup,
    jsonify,
    abort,

)
from flask_pymongo import PyMongo
import datetime
import pytz
app = Flask(__name__)
line_bot_api = LineBotApi('MuR72Xn+KcIDblzlw8RI+v9msVbC3f+vpa7wpBjT1rpdvXtWdgz7lvs4g837yrGXsV7/RneVMolyS/tBHR6dN+rh3zGQEM6w4yYcKWzGQvAOyYFyQslivchW5cwu+H5diHT8zaiFIlEqlzMJU86uMgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('df9689715ac16dd5795f9d0c4e4aba57')

app.config['MONGO_URI'] = 'mongodb+srv://sawaembed:212224236@sawatech.1rufs.mongodb.net/embedded'
mongo = PyMongo(app)

collection_test = mongo.db.test
collection_userData = mongo.db.user_data
collection_petStatus = mongo.db.pet_status

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/register')
def register():
    return render_template("register_form.html")

@app.route('/create_user', methods=['POST'])
def create_user(**kwargs):
    userData = {
        "userID": kwargs["userID"],
        "serialID": "0",
        "name":"0",
        "petName":"0",
        "tel" : "0"
    }
    collection_userData.insert_one(userData)
    return userData

@app.route('/get_userid', methods=['GET'])
def who_u_talk_to(**kwargs):
    line_bot_api.reply_message(kwargs["replyToken"], TextSendMessage(text='https://average-wolverine-93.loca.lt/register'))
    return {"userID":kwargs["userID"]}

@app.route('/delete_user', methods=['DELETE'])
def delete_user(**kwargs):
    userID = {"userID": kwargs["userID"]}
    petStatus = collection_userData.find(userID)
    serialID = {"serialID":petStatus[0]["serialID"]}
    collection_userData.delete_many(userID)
    collection_petStatus.delete_many(serialID)
    return {'result': 'Deleted successfully'}

@app.route('/register_user', methods=['PATCH'])
def register_user():
    data = request.form
    userData = {
        "userID": data["userID"],
        "serialID": data["serialID"],
        "name":data["name"],
        "petName": data["petName"],
        "tel": data["tel"]
    }

    petStatus = {
        "serialID": data["serialID"],
        "petName":data["petName"],
        "temp": '0',
        "humid": '0',
        "location": '0'
    }

    collection_userData.update_one(userData)
    collection_petStatus.insert_one(petStatus)
    return {'result': 'Crated successfully'}

@app.route('/userdata', methods=['PATCH'])
def edit_userdata():
    data = request.json    
    filt = {'userID': ""}
    updated_content = {"$set": {'content1': data["content1"]}}  
    collection_userData.update_one(filt, updated_content) 
    return {'result': 'Updated successfully'}

@app.route('/userdata', methods=['GET'])
def get_userdata():
    filt = {"serialID":"test1"}
    data = collection_petStatus.find_one(filt)
    userData = {
        "userID": data["userID"],
        "serialID": data["serialID"],
        "name":data["name"],
        "petName": data["petName"],
        "tel": data["tel"]
    }
    return userData

@app.route('/test', methods=['POST'])
def test():
    data = request.json
    collection_test.insert_one(data)
    return {'result': 'Created successfully'}

@app.route('/petStatus', methods=['POST'])
def petStatus():
    data = request.json
    filt = {'serialID': '1'}
    petStatus = {
        "serialID": data["serial_ID"],
        "temp": data["temp"],
        "humid": data["humid"],
        "location": data["location"]
    }
    collection_petStatus.update_one(filt,petStatus)
    return {'result': 'Created successfully'}


@app.route('/GPS', methods=['GET', 'POST'])
def checkinfo(**kwargs):
    NamePet = collection_userData.find({"petName":kwargs['nameCat'],"userID":kwargs['userID']})
    print(NamePet[0]["serialID"])
    SerialID = NamePet[0]["serialID"]
    Status = collection_petStatus.find({"serialID":SerialID})
    PetInfo = Status[0]
    print(PetInfo)
    print(type(PetInfo))
    line_bot_api.reply_message(kwargs['replyToken'], TextSendMessage(text = str(PetInfo) ))
        


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

@handler.add(FollowEvent)
def handle_follow(event):
    userID = event.source.user_id
    return create_user(userID = userID)

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    userID = event.source.user_id
    return delete_user(userID = userID)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    userID = event.source.user_id
    nameCat = event.message.text
    replyToken = event.reply_token
    
    if text == 'เมนู':
        return who_u_talk_to(replyToken=replyToken, userID = userID)
    else:
        return checkinfo(replyToken=replyToken,userID=userID,nameCat=nameCat)
        
    #else:
    #   return line_bot_api.reply_message(replyToken,TextSendMessage(text='ลองคำสั่งอื่น'))

if __name__ == '__main__':
    app.run(port='8000',debug=True)

