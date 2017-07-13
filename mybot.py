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
    username, group_name = group_choice_strict(info)
    if group_name:
        group = itchat.search_chatrooms(group_name)[0]
        group.add_member([{'UserName': username}])

'''
@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def msg_text_reply(info):
    print(info['Content'])
'''


@itchat.msg_register(itchat.content.FRIENDS)
def msg_add_friend(info):
    print('aaaaaaaaa')
    # QInfo.put(info)
    username, alias, nickname, groups, mark = info_add(info)                # 分析信息，分类
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
    else:
        print('no groups')
        itchat.send(msg_greet['friend_group'].format(alias=alias), username)


@itchat.msg_register(itchat.content.NOTE, isGroupChat=True)
def msg_group_note(info):
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


itchat.auto_login(hotReload=True)
if __name__ == '__main__':
    itchat.run()
