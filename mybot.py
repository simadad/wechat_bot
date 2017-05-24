#!/usr/local/bin/python3.5
# coding: utf8
from processor import info_router
import itchat


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_msg_reply(info):
    reply_msg = info_router(info)
    if reply_msg:
        return reply_msg


def send_img(img, username):
    itchat.send('@img@%s' % img, username)


def send_text(msg, username):
    itchat.send(msg, username)


itchat.auto_login(enableCmdQR=2, hotReload=True)
if __name__ == '__main__':
    itchat.run()

