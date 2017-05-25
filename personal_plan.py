#!/usr/local/bin/python3.5
from statistic import db as info_db
from getQA import db as chat_db
from getQA import db_table_column, data_save
db_table_column['user_wechat'] = 'username, wechat'


def search_students():
    """
    搜索并返回符合条件的学生用户名，生成器形式
    :return:
    """
    cur = info_db.cursor()
    cur.execute('''
        #TODO
    ''')
    yield cur.fetchall()


def search_wechat(username):
    """
    接受username，返回微信最新UserName
    :return:
    """
    cur = chat_db.cursor()
    cur.execute('''
        SELECT wechat FROM user_wechat WHERE username='{username}'
        ;'''.format(username=username))
    wechat = cur.fetchone()
    wechat_username = _get_new_wechat(username, wechat)
    return wechat


def _get_new_wechat(username, wechat):
    """
    搜索并储存微信
    :return:
    """

    return


def comb_info():
    """
    组合信息，返回消息模版
    :return:
    """


def send_msg():
    """
    发送消息
    :return:
    """


def run():
    """
    search_students -> search_wechat -> comb_info -> send_msg
    :return:
    """

if __name__ == '__main__':
    run()
