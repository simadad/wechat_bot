from MyWechatBot import getQA
QuestionHint = r'#Q#'
AnswerHint = r'#A#'


def qa_coroutine():
    info = ''
    while True:
        info = yield
        pass


def question_line(info, name):
    pass


def pure_msg(info):
    """
    获取消息，返回纯净内容
    """
    if info['MsgType'] == 1:
        msg = info['Content']
    else:
        msg = info['Text']
    return msg


def info_router(info):
    """
    接收信息，分析消息类型，分发处理
    返回回复信息
    """
    for i in info:
        print(i, info[i])
    # print(info['ActualNickName'], ':', info['Text'])
    msg = pure_msg(info)
    if msg.startswith(QuestionHint):
        # question_line(msg, info['ActualNickName'])
        getQA.save_question(msg)
    elif msg.startswith(AnswerHint):
        getQA.save_answer(msg)
        return 'question saved'
