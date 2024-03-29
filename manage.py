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
    return 'Sawa Embedded'

@app.route('/register/<userID>')
def register_page(userID):
    return render_template("register.html",userID=userID)

@app.route('/create_user', methods=['POST'])
def register():
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
        "lat": '0',
        "long": '0'
    }
    collection_userData.insert_one(userData)
    collection_petStatus.insert_one(petStatus)
    return 'Created Successfully'

@app.route('/userdata', methods=['GET'])
def get_userData():
    data = collection_userData.find()
    userData = []
    for element in data:
        userData.append({
            "userID": element["userID"],
            "serialID": element["serialID"],
            "name":element["name"],
            "petName": element["petName"],
            "tel": element["tel"]
        })
    return jsonify(userData)

@app.route('/petStatus', methods=['GET'])
def get_petStatus():
    data = collection_petStatus.find()
    petStatus = []
    for element in data:
        petStatus.append({
            "serialID": element["serialID"],
            "petName": element["petName"],
            "temp": element["temp"],
            "humid": element["humid"],
            "lat": element["lat"],
            "long": element["long"]
        })
    return jsonify(petStatus)

@app.route('/userdata/userID/<userID>', methods=['GET'])
def get_userdata_by_userID(userID):
    filt = {"userID":userID}
    data = collection_userData.find(filt)
    userData = []
    for element in data:
        userData.append({
            "userID": element["userID"],
            "serialID": element["serialID"],
            "name":element["name"],
            "petName": element["petName"],
            "tel": element["tel"]
        })
    return jsonify(userData)

@app.route('/userdata/serialID/<serialID>', methods=['GET'])
def get_userdata_by_serialID(serialID):
    filt = {"serialID":serialID}
    data = collection_userData.find_one(filt)
    userData = {
        "userID": data["userID"],
        "serialID": data["serialID"],
        "name":data["name"],
        "petName": data["petName"],
        "tel": data["tel"] 
    }
    return jsonify(userData)

@app.route('/petStatus/<serialID>', methods=['PUT'])
def get_petStatus_from_hardware(serialID):
    data = request.json
    serialID = {'serialID':str(serialID)}
    update_petStatus = {
        "$set":{
            "serialID": str(data["serialID"]),
            "petName": str(data["petName"]),
            "temp": str(data["temp"]),
            "humid": str(data["humid"]),
            "lat": str(data["lat"]),
            "long": str(data["long"])
        }
    }
    collection_petStatus.update_one(serialID,update_petStatus)
    temp = collection_petStatus.find_one(serialID)
    userdata = collection_userData.find_one(serialID)
    userID = userdata["userID"]
    petName = userdata["petName"]
    temp = temp["temp"]
    if(float(temp) >= 30):
        line_bot_api.push_message(userID, TextSendMessage(text = petName + "ของคุณมีอุณหภูมิสูงผิดปกติ !!"))
    return {'result': 'Updated Successfully'}

@app.route('/delete_data', methods=['DELETE'])
def delete_data(**kwargs):
    userID = {"userID": kwargs["userID"]}
    userData = collection_userData.find(userID)
    for element in userData:
        serialID = {"serialID":element["serialID"]}
        collection_petStatus.delete_many(serialID)
    collection_userData.delete_many(userID)
    return {'result': 'Deleted successfully'}

@app.route('/information', methods=['GET', 'POST'])
def checkinfo(**kwargs):
    NamePet = collection_userData.find({"petName":kwargs['nameCat'],"userID":kwargs['userID']})
    SerialID = NamePet[0]["serialID"]
    Status = collection_petStatus.find({"serialID":SerialID})
    PetInfo = Status[0]
    temp = str(PetInfo["temp"])
    humid = str(PetInfo["humid"])
    if(PetInfo["lat"] == "0"):
        line_bot_api.push_message(kwargs['userID'], TextSendMessage(text = 'รอสักครู่ กำลังหาน้องแมวให้อยู่น้า'))
    else:
        line_bot_api.push_message(kwargs['userID'], LocationSendMessage(title ='cat location' , latitude= PetInfo["lat"],longitude=PetInfo["long"],address="ตำแหน่งของ " + PetInfo["petName"]))
    line_bot_api.push_message(kwargs['userID'], TextSendMessage(text = 'Name: ' + PetInfo["petName"] + "\n" + 'Temperature: ' + temp + "\n" +'humidity: ' + humid ))
    # --------------- test api ----------------


# * ------------------------------------ line api ---------------------------------- *

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

# @handler.add(FollowEvent)
# def handle_follow(event):
#     userID = event.source.user_id
#     return create_user(userID = userID)

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    userID = event.source.user_id
    return delete_data(userID = userID)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    userID = event.source.user_id
    nameCat = event.message.text
    replyToken = event.reply_token
    listPet = []
    for name in collection_userData.find({"userID":userID}):        
        listPet.append(name["petName"])
    if text == 'ลงทะเบียน':
        return line_bot_api.reply_message(replyToken, TextSendMessage(text = 'ลงทะเบียนได้ที่ลิงก์นี้เลยจ้า ' + 'https://polite-mole-50.loca.lt/register/' + userID))
    # if text == 'แก้ไข':
    #     return line_bot_api.reply_message(replyToken, TextSendMessage(text = 'https://cuddly-zebra-7.loca.lt/edit/' + userID))
    #---------------------------------- check ว่าสัตว์ชื่อนี้มีอยู่ในดาต้าเบสหรือยัง ------------------------------------
    else:
        NamePet = collection_userData.find({"petName":text,"userID":userID})
        for x in listPet:
            
            if(text == x):
                return checkinfo(replyToken=replyToken,userID=userID,nameCat=nameCat)
            else:
                pass
        if(len(listPet)==0):
            return  line_bot_api.reply_message(
                        event.reply_token, [
                            TextSendMessage(
                                text='ไม่มีสัตว์เลี้ยงตัวนี้อยู่ในระบบ กรุณาลงทะเบียนก่อน https://polite-mole-50.loca.lt/register/' + userID
                            )
                        ]
                    )
        else:
            line_bot_api.push_message(userID, TextSendMessage(text=('ลองพิมพ์ชื่อสัตว์เลี้ยงของคุณ')))
            for x in listPet:
                line_bot_api.push_message(userID,TextSendMessage(text= x))
if __name__ == '__main__':
    app.run(port='8000',debug=True)

# ----------------- set Hardware --------------------------
# @app.route('/set_serialID', methods=['POST'])
# def set_serialID():
#     data = request.json
#     userData = {
#         "userID":"",
#         "serialID": data["serialID"],
#         "name":"",
#         "petName":"",
#         "tel":""
#     }
#     petStatus = {
#         "serialID": data["serialID"],
#         "petName":"",
#         "temp": '0',
#         "humid": '0',
#         "lat": '0',
#         "long": '0'
#     }
#     collection_userData.insert_one(userData)
#     collection_petStatus.insert_one(petStatus)
#     return 'Setup Success!'

# <--------------- real register -----------------> 
# @app.route('/create_user', methods=['POST','PUT'])
# def create():
#     data 
