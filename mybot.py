from processor import info_router
import itchat

'''
def msg_reply():
    while True:
        info = yield
        reply_msg = info_router(info)
        itchat.send(reply_msg, info['FromUserName'])
'''


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_msg_reply(info):
    reply_msg = info_router(info)
    return reply_msg
'''
    if msg['MsgType'] == 1:
        if msg['isAt']:
            print(msg['ActualNickName'], ':', msg['Text'])
            reply_msg = info_router(msg)
            return reply_msg
    else:
    '''


if __name__ == '__main__':
    itchat.auto_login()
    itchat.run()
