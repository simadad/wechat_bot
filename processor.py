#!/usr/local/bin/python3.5
from MyWechatBot import getQA
import datetime
import re
QuestionHint = r'#Q#'                   # 提问
AnswerHint = r'#A#'                     # 回答
# Continue = r'#C#'                       # 继续描述上个问题
question_time = 3600                     # 提问持续时间，单位秒
QABars = {}

'''
协程内处理思路：
if #Q# -> 开启新问题，储存，得到 ID，<答案搜索>,返回答案（空）；
if #A# -> 储存，得到 ID ，储存关系
'''


def get_reply(msg, isa, qid):
    # TODO 完善返回信息，ID + answer
    if isa:
        # aid = getQA.save_answer(msg, qid)
        getQA.save_answer(msg, qid)
        return None                      # TODO 标签分析与答案检索
    else:
        # did = getQA.save_desc(msg, qid)
        getQA.save_desc(msg, qid)
        return 'answer to be add', qid


def question_bar():
    """
    协程
    """
    qid = getQA.save_question()
    print('bar: ', qid)
    reply = ''
    while True:
        msg, isa = yield reply
        reply = get_reply(msg, isa, qid)


def get_bar(name, isq):
    """
    建立以 UserName 为关键字，以协程为值的字典，存储协程
    返回对应协程
    """
    now_time = datetime.datetime.now()
    print('get_bar: ', name)
    if isq:
        QABars[name] = [question_bar(), now_time]
        QABars[name][0].send(None)
        print(11111, QABars[name])
    elif name in QABars and now_time - QABars[name][1] < datetime.timedelta(0, question_time):
            QABars[name][1] = now_time                  # TODO 命名元组
    else:
        return None                                           # TODO 超时、未加标识符提示
    return QABars[name][0]

'''
def get_qa_line():
    name = ''
    while True:
        if name in QABars:
            yield QABars[name]
        else:
            QABars[name] = question_bar()
            QABars[name].send(None)
            question_start = datetime.datetime.now()
            yield QABars[name]
'''


def pure_msg(info):
    """
    清洗消息
    """
    isq = False
    isa = False
    if info['MsgType'] == 1:
        if 'ActualNickName' in info:
            name = info['ActualNickName']
            pre_msg = info['Content']
        elif info['Content'].startswith('@'):
            name = re.findall(r'^@(\S+)\s', info['Content'])[0]
            pre_msg = info['Content'].lstrip('@%s' % name)
        else:
            name = ''
            pre_msg = ''
    else:
        name = info['FromUserName']
        pre_msg = info['Text']

    if pre_msg.startswith(QuestionHint):
        isq = True
        msg = pre_msg.lstrip(QuestionHint)
    elif pre_msg.startswith(AnswerHint):
        isa = True
        msg = pre_msg.lstrip(AnswerHint)
    else:
        msg = pre_msg
    return name, msg, isq, isa


def info_router(info):
    """
    接收信息，分析消息类型，分发处理
    返回回复信息
    """
    for i in info:
        print(i, info[i])
    print('============')
    # print(info['ActualNickName'], ':', info['Text'])
    name, msg, isq, isa = pure_msg(info)
    if name:
        bar = get_bar(name, isq)                         # 获取对应协程
    else:
        bar = None
    if bar:
        reply = bar.send((msg, isa))                       # 发送信息，获取信息处理结果
        return reply
    else:
        return None                                     # TODO 超时处理

'''
    if msg.startswith(QuestionHint):
        bar = get_bar(name)
        answer = bar.send(msg)
        # question_line(msg, info['ActualNickName'])
        # getQA.save_question(msg)
    elif msg.startswith(AnswerHint):
        bar = get_bar(name)
        bar.send(msg)
        # getQA.save_answer(msg)
        return 'question saved'
    '''

# TODO  Tag制作与答案搜索
# TODO  定时或触发式自动删除问题协程
# TODO  END 参数结束问题
