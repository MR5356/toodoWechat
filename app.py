from flask import Flask, request, abort
from WechatMP import WechatMP
import xmltodict

app = Flask(__name__)
Token = ''
appId = ''
secret = ''
wmp = WechatMP(Token=Token, appId=appId, secret=secret)


@app.before_request
def checkSignature():
    signature = request.values.get('signature')
    timestamp = request.values.get('timestamp')
    nonce = request.values.get('nonce')
    echostr = request.values.get('echostr')  # 仅在验证服务器时使用次参数
    if not wmp.checkSignature(timestamp=timestamp, nonce=nonce, signature=signature):
        abort(404)
    if echostr:
        return echostr


@app.route('/')
def main():
    msg = xmltodict.parse(request.data).get('xml')
    msgType = msg.get('MsgType')
    res = wmp.replyText(msg, 'Hi~ 终于等到你啦')
    if msgType == 'text':
        res = wmp.replyText(msg, msg.get('Content'))
    if msgType == 'image':
        res = wmp.replyImage(msg, msg.get('MediaId'))
    """ And More Type of Message"""
    if msgType == 'event':
        if msg.get('Event') == 'subscribe':
            # 关注后回复
            res = wmp.replyText(msg, 'Hi~\n终于等到你啦')
    return xmltodict.unparse(res)


if __name__ == '__main__':
    app.run(port=8001)
