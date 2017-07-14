#!/usr/local/bin/python3.5
# coding: utf8
from processor import info_router, info_add, msg_greet, group_choice_strict
import itchat
import re
# from queue import Queue
#
# QInfo = Queue()


# @itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
# def text_msg_reply(info):
#     reply_msg = info_router(info)
#     if reply_msg:
#         return reply_msg


@itchat.msg_register(itchat.content.TEXT, isFriendChat=True)
def msg_group_choice(info):
    """
    好友消息处理，严格入群规则
    """
    # username, group_or_index, is_index = group_choice_strict(info)
    mode, reply = group_choice_strict(info)
    if mode == 'lab':
        username, alias, groups, mark = reply
        itchat.search_friends(userName=username).set_alias(mark + alias)  # 设置备注名
        for group_name in groups:
            print('mybot add group name：', group_name)
            group = itchat.search_chatrooms(group_name)[0]
            print('mybot group', group)
            group.add_member([{'UserName': username}])  # 发送群邀请
        itchat.send(msg_greet['bind'], username)
    elif mode == 'msg':
        username, msg = reply
        itchat.send(msg, username)
    elif mode == 'strict':
        username, group_name = reply
        group = itchat.search_chatrooms(group_name)[0]
        group.add_member([{'UserName': username}])  # 发送群邀请

'''
@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def msg_text_reply(info):
    print(info['Content'])
'''


@itchat.msg_register(itchat.content.FRIENDS)
def msg_add_friend(info):
    """
    好友申请处理，宽松入群规则
    """
    print('aaaaaaaaa')
    # QInfo.put(info)
    username, alias, groups, mark = info_add(info)                # 分析信息，分类
    itchat.add_friend(username, status=3)                                   # 添加好友
    itchat.send(msg_greet['friend'].format(alias=alias), username)          # 发送好友欢迎消息
    itchat.search_friends(userName=username).set_alias(mark + alias)         # 设置备注名
    if groups:
        for group_name in groups:
            print('mybot add group name：', group_name)
            group = itchat.search_chatrooms(group_name)[0]
            print('mybot group', group)
            group.add_member([{'UserName': username}])                      # 发送群邀请
            # group.send(msg_greet['group'].format(nickname=nickname))        # 发送群友欢迎消息
    # else:
    #     print('no groups')
    #     itchat.send(msg_greet['friend_group'].format(alias=alias), username)


@itchat.msg_register(itchat.content.NOTE, isGroupChat=True)
def msg_group_note(info):
    """
    群欢迎信息
    """
    alias = re.findall(r'你邀请"(.+)"加入了群聊', info['Content'])
    username = info['FromUserName']
    if alias:
        users = itchat.search_friends(remarkName=alias[0])
        if len(users) == 1:
            user = users[0]
            nickname = user['NickName']
            itchat.send(msg_greet['group'].format(nickname=nickname), username)


def send_img(img, username):
    itchat.send('@img@%s' % img, username)


def send_text(msg, username):
    itchat.send(msg, username)


itchat.auto_login(hotReload=True, enableCmdQR=2)
if __name__ == '__main__':
    itchat.run()
