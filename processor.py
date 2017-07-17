#!/usr/local/bin/python3.5
import getQA
import datetime
import re
# import jieba
import requests
import json
import pymysql

# db = pymysql.connect('localhost', 'marklab', 'crossinlab2017', 'crossin_lab', charset="utf8")

QuestionHint = r'#Q#'                   # 提问
AnswerHint = r'#A#'                     # 回答
# Continue = r'#C#'                       # 继续描述上个问题
question_time = 3600                     # 提问持续时间，单位秒
QABars = {}
url_verify = 'http://crossincode.com/vip/verify/wechat/'
key_verify = "verifywechatkey$123456"

# labMark = {
#     'lab': r'#lab#',
#     'spider': r'#spi#',
#     'base': r'#bas#',
#     'etc': r'#etc#'
# }
# groupKey = {
#     '爬虫交流群': {'爬虫'},
#     '进阶交流群': {'进阶', '提高', '高级'},
# }
# groupKeyList = [
#     ('新手', ['新手交流群']),
#     ('爬虫', ['爬虫交流群']),
#     ('进阶', ['进阶交流群'])
# ]
# groupKeyDefault = '新手交流群'
# labAddChar = r'#lab#'
# labCrmChar = r'#lab#'
# groupMark = r'$G$'
# group = {
#     labChar: '答疑群-2017-2',
# labAddChar: 'B',
#
# }
# groups2 = {
#     groupMark + '1': '2017成长群',
#     groupMark + '2': '2017进阶群',
#     groupMark + '3': '2017爬虫群'
# }
# groups = """
# 代码    群名\n
# {groupMark}1    2017成长群\n
# {groupMark}2    B\n
# {groupMark}3    2017进阶群\n
# 请输入完整代码，例如 {groupMark}3
# """.format(groupMark=groupMark)
# TODO 加入微信配置页面
msg_greet = {
    'friend': '''{alias}，你好！
欢迎加入Crossin的编程教室。

加入读者交流公共群请回复 1000
“码上行动”用户加群请回复 2000

学习资源目录 http://crossincode.com/home/

此账号为机器人，问答功能正在开发中。如操作过程中有任何问题，可在公众号后台留言，或联系微信 crossin11。复杂的代码问题请在 bbs.crossincode.com 上发帖提问，附上完整的代码、输出、运行环境说明等。''',
    'group': '欢迎新同学：{nickname}！',
    # 'friend_group': '您好，{alias}\n回复 0000 查看入群代码。',
    'bind': '已成功绑定账号：{alias} ！',
    'unbind': '绑定失败，验证码三分钟内有效，请重试。',
    # 'ques': '您好，{nickname}，请输入您要申请的群代码\n%s' % groups
}
msg_router = {
    '1000': '发送代码加入对应群组：\n{index}',
    '2000': '''参与码上行动的同学，请点击课程首页上“答疑群”-“关联微信及入群说明”，
        查看绑定方法和状态。如尚未绑定，请直接在此回复个人验证码。''',
}
friend_mark = {
    'lab': '#lab#',
    'etc': '#etc#',
}

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


def group_choice_vip(code, nickname):
    """
    付费用户调取后台接口，获取网站用户名，应加群名
    :return: (username, groups)/ (False, False)
    """
    json_info = {
        "key": key_verify,
        "code": code,
        "wechat": nickname
    }
    r = requests.post(url_verify, json=json_info)
    back_info = json.loads(r.text)
    print('back_info', back_info)
    print('type', type(back_info))
    if 'username' in back_info:
        return back_info['username'], back_info['group']
    else:
        return False, False


def get_rules():
    """
    数据库获取关键字对应群规则
    :return: (关键字, 群名)
    """
    db = pymysql.connect('localhost', 'marklab', 'crossinlab2017', 'crossin_lab', charset="utf8")
    cur = db.cursor()
    cur.execute('''
        SELECT keyword, nickname FROM webotconf_ruleaddfriend rule
        JOIN webotconf_chatroom room ON room.id = rule.chatroom_id
        WHERE room.order < 100
        ORDER BY room.order
    ''')
    return cur.fetchall()


def get_strict_rules():
    """
    严格入群规则，数据库
    :return:[(代码，#群名),]
    """
    db = pymysql.connect('localhost', 'marklab', 'crossinlab2017', 'crossin_lab', charset="utf8")
    cur = db.cursor()
    cur.execute('''
        SELECT keyword, nickname FROM webotconf_ruleaddfriend rule
        JOIN webotconf_chatroom room ON room.id = rule.chatroom_id
        WHERE room.order > 100
        ORDER BY room.order
    ''')
    return cur.fetchall()


def group_choice(msg):
    """
    非付费用户分流
    """
    # msg_set = set(jieba.cut(msg, cut_all=True))
    # for key in groupKey:
    #     if groupKey[key] & msg_set:
    #         return key
    # else:
    #     return groupKeyDefault
    rules = get_rules()
    for rule in rules:
        print('rule', rule)
        if rule[0] in msg:
            return [rule[1]]
    else:
        return False


def _get_index():
    rules = get_strict_rules()
    index = ''
    for rule in rules:
        index += '\n{code:<6}{group}\n'.format(code=rule[0], group=rule[1])
    return index


def group_choice_strict(info):
    """
    严格入群规则，消息处理
    :return: 不处理/代码目录/对应规则
    """
    msg = info['Content'].strip()
    username = info['FromUserName']
    nickname = info['User']['NickName']
    print('msg: ', msg)
    print('username:', username)
    print('nickname', nickname)
    if re.match(r'\d{6}', msg):
        alias, groups = group_choice_vip(msg, nickname)
        print('VIP-alias-groups: ', alias, groups)
        if alias:
            mark = friend_mark['lab']
            return 'lab', (username, alias, groups, mark)
        else:
            return 'msg', (username, msg_greet['unbind'])
    elif msg in msg_router:
        return 'msg', (username, msg_router[msg].format(index=_get_index()))
    rules = get_strict_rules()
    for rule in rules:
        print(rule)
        if msg == rule[0]:
            return 'strict', (username, rule[1].lstrip('#'))
    else:
        return False, False


def info_add(info):
    """
    好友添加认证
    """
    username = info['RecommendInfo']['UserName']
    msg = info['RecommendInfo']['Content']
    nickname = info['RecommendInfo']['NickName']
    mark = friend_mark['etc']
    alias = nickname
    if re.match(r'\d{6}', msg.strip()):
        alias, groups = group_choice_vip(msg.strip(), nickname)
        print('alias-groups: ', alias, groups)
        if groups:
            mark = friend_mark['lab']
    else:
        groups = group_choice(msg.strip())
        print('group_chose', groups)
    return username, alias, groups, mark


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
