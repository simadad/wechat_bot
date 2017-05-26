#!/usr/local/bin/python3.5
import itchat
from statistic import db as info_db
from getQA import db as wechat_db
from getQA import db_table_column, data_save
import datetime
db_table_column['user_wechat'] = 'username, wechat, new_wechat'
itchat.auto_login(hotReload=True)


def search_students_info():
    """
    搜索并返回符合条件的学生用户名，生成器形式
    :return:
    """
    cur = info_db.cursor()
    cur.execute('''
    SELECT user.username, bill.wechat, vip.remind_days, plan.start_date, plan.end_date, SUM(lesson.hour)
    FROM school_learnedlesson learned
    LEFT JOIN school_lesson lesson
    ON lesson.id = learned.lesson_id
    LEFT JOIN auth_user user
    ON user.id = learned.user_id
    LEFT JOIN school_plan plan
    ON user.id = plan.user_id
    LEFT JOIN vip_premium vip
    ON user.id = vip.user_id
    LEFT JOIN vip_bill bill
    ON user.id = bill.vip_user_id
    WHERE vip.remind_plan = true
    OR vip.remind = true
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
        wechat_id = _confirm(stu_info)
        # if new_wechat:
        #     we_user = itchat.search_friends(new_wechat)
        #     wechat_id = we_user['UserName']
        # else:
        #      wechat_id = False
    return wechat_id


def _confirm(stu_info):
    """
    本地数据库确认可用微信号
    :return:
    """
    # username, wechat = stu_info
    # cur = wechat_db.cursor()
    # cur.execute('''
    #         SELECT username, new_wechat FROM user_wechat WHERE username='{username}'
    #         ;'''.format(username=username))
    # _, new_wechat = cur.fetchone()
    # if new_wechat is None:
    #     values = "'{}', '{}', null".format(*stu_info)
    #     data_save('user_wechat', values)
    #     new_wechat = False
    # return new_wechat
    return False


def comb_info(wechat_id, whole_hours, info):
    """
    组合信息，返回消息模版
    :return:
    """
    username, _, start_time, end_time, course_id, rate, present_lesson, learned_hours = info
    aim_lesson = _get_aim_lesson(whole_hours, learned_hours, end_time, present_lesson)
    model = _model_choice(whole_hours, start_time, end_time)
    msg = _get_msg(username, aim_lesson, model)
    return msg


def _get_whole_hours():
    """
    获取总课时
    """
    hours = 0
    return hours


def _get_aim_lesson(whole_hours, learned_hours, end_time, present_lesson):
    """
    计算目标课程
    """
    now = datetime.datetime.now()
    aim_lesson = ''
    return aim_lesson


def _model_choice(whole_hours, start_time, end_time):
    """
    选择消息模版
    """
    model = ''
    return model


def _get_msg(username, aim_lesson, model):
    """
    组合消息
    """
    msg = ''
    return msg


def send_msg(wechat_id, msg):
    """
    发送消息
    :return:
    """
    itchat.send(msg, wechat_id)


def run():
    """
    search_students_info -> search_wechat -> comb_info -> send_msg
    """
    whole_hours = _get_whole_hours()
    students_info = search_students_info()
    for stu_info in students_info:
        wechat_id = search_wechat_id(stu_info[:2])
        if wechat_id:
            msg = comb_info(wechat_id, whole_hours, stu_info)
            send_msg(wechat_id, msg)

if __name__ == '__main__':
    run()
