from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from flask import Flask, request, abort
app = Flask(__name__)
line_bot_api = LineBotApi('MuR72Xn+KcIDblzlw8RI+v9msVbC3f+vpa7wpBjT1rpdvXtWdgz7lvs4g837yrGXsV7/RneVMolyS/tBHR6dN+rh3zGQEM6w4yYcKWzGQvAOyYFyQslivchW5cwu+H5diHT8zaiFIlEqlzMJU86uMgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('df9689715ac16dd5795f9d0c4e4aba57')
@app.route('/')
def index():


    return 'Hello World!'
@app.route('/GPS', methods=['GET', 'POST'])
def checkgps(**kwargs):
    return line_bot_api.reply_message(kwargs['replyToken'], TextSendMessage( text = 'แมวอยู่ @Address นี่ครับ' ))

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
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    text = event.message.text
    
    replyToken = event.reply_token
    #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
# Rich Menu Switcher
    if(text == 'register'):
        return line_bot_api.reply_message(replyToken,TextSendMessage(text='กรุณากรอกชื่อแมว'))
    if(text == 'check gps'):
        return checkgps(replyToken=replyToken)
    if(text == 'check temperature'):
        return Temp(replyToken=replyToken)
    else:
        return line_bot_api.reply_message(replyToken,TextSendMessage(text='ลองคำสั่งอื่น'))

if __name__ == '__main__':
    app.run(debug=True)

