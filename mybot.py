from processor import info_router
import itchat


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_msg_reply(info):
    """
    信息类型过滤，提取文字信息，提交router分发处理
     获取返回信息，回复消息
    """
    reply_msg = info_router(info)
    return reply_msg


if __name__ == '__main__':
    itchat.auto_login()
    itchat.run()
