#!/usr/local/bin/python3.5
import itchat
from statistic import db as info_db
from getQA import db as wechat_db
from getQA import db_table_column, data_save
db_table_column['user_wechat'] = 'username, wechat, new_wechat'
itchat.auto_login(hotReload=True)


def search_students_info():
    """
    搜索并返回符合条件的学生用户名，生成器形式
    :return:
    """
    cur = info_db.cursor()
    cur.execute('''
    SELECT MAX(chapter.seq), COUNT(lesson.seq), user.username
    FROM school_learnedlesson learned
    LEFT JOIN school_lesson lesson
    ON lesson.id = learned.lesson_id
    LEFT JOIN auth_user user
    ON user.id = learned.user_id
    LEFT JOIN school_chapter chapter
    ON chapter.id = lesson.chapter_id
    WHERE user.username = '{username}'
    GROUP BY user.username
    ''')
    for row in cur:
        yield row


def search_wechat_id(stu_info):
    """
    接受username，返回微信最新UserName
    :return:
    """
    username, wechat = stu_info
    we_user = itchat.search_friends(wechat) or itchat.search_friends(username)
    if len(we_user) == 1:
        wechat_id = we_user['UserName']
    else:
        new_wechat = _confirm(stu_info)
        if new_wechat:
            we_user = itchat.search_friends(new_wechat)
            wechat_id = we_user['UserName']
        else:
             wechat_id = False
    return wechat_id


def _confirm(stu_info):
    """
    本地数据库确认可用微信号
    :return:
    """
    username, wechat = stu_info
    cur = wechat_db.cursor()
    cur.execute('''
            SELECT username, new_wechat FROM user_wechat WHERE username='{username}'
            ;'''.format(username=username))
    _, new_wechat = cur.fetchone()
    if new_wechat is None:
        values = "'{}', '{}', null".format(*stu_info)
        data_save('user_wechat', values)
        new_wechat = False
    return new_wechat


def comb_info(wechat_id, info):
    """
    组合信息，返回消息模版
    :return:
    """
    username, _, start_time, end_time, course_id, rate = info



def send_msg():
    """
    发送消息
    :return:
    """


def run():
    """
    search_students_info -> search_wechat -> comb_info -> send_msg
    :return:
    """
    students_info = search_students_info()
    for stu_info in students_info:
        wechat_id = search_wechat_id(stu_info[:2])

if __name__ == '__main__':
    run()
