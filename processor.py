from MyWechatBot import getQA


def question_processor(msg):
    pass


def answer_processor(msg):
    pass


def info_router(info):
    print(2222, info, 222)
    print(info['ActualNickName'], ':', info['Text'])
    if info['MsgType'] == 1:
        if info['isAt']:
            msg = info['Content']
        else:
            msg = None
    else:
        msg = info['Text']
    if msg:
        getQA.save_question(msg)
        return 'question saved'

