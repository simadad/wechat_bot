#!/usr/local/bin/python3.5
import itchat
import datetime
from statistic import db as info_db
from getQA import db as wechat_db
from getQA import db_table_column, data_save
db_table_column['user_wechat'] = 'username, wechat, new_wechat'
db_table_column['schedule'] = 'course_id, schedule, title, accumulate_hours'
itchat.auto_login(hotReload=True)
courses = ('1', '2')


def search_students_info(course_id):
    """
    搜索并返回符合条件的信息生成器
    网站用户名-微信号-推送频率-计划起始日-计划到期日-总课时
    :return:
    """
    cur = info_db.cursor()
    cur.execute('''
    SELECT user.username, bill.wechat, vip.remind_days, COUNT(learned.lesson_id),
    plan.start_date, plan.end_date, plan.course_id, SUM(lesson.hour)
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
    AND plan.course_id = '{course_id}'
    GROUP BY user.username
    '''.format(course_id=course_id))
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
        # print(we_user)
        # print(we_user[0])
        wechat_id = we_user[0]['UserName']
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
    SELECT user.username, bill.wechat, vip.remind_days, COUNT(learned.lesson_id),
    plan.start_date, plan.end_date, plan.course_id, SUM(lesson.hour)
    """
    username, _, remind_days, present_lessons, start_date, end_date, course_id, learned_hours = info
    aim_lesson = _get_aim_lesson(whole_hours, learned_hours, end_date, present_lessons)
    model = _model_choice(whole_hours, start_date, end_date)
    msg = _get_msg(username, aim_lesson, model)
    return msg


def _get_whole_hours(course_id):
    """
    获取总课时
    """
    cur = info_db.cursor()
    cur.execute('''
        SELECT SUM(lesson.hour)
        FROM school_lesson lesson
        LEFT JOIN school_chapter chapter
        ON lesson.chapter_id = chapter.id
        WHERE chapter.course_id = '{course_id}'
    '''.format(course_id=course_id))
    hours = cur.fetchone()
    return hours


def _get_aim_lesson(whole_hours, learned_hours, end_date, present_lesson):
    """
    计算目标课程
    """
    now = datetime.datetime.now()
    days = (end_date - now).days
    rest_hours = whole_hours - learned_hours
    learned_hours += rest_hours / days
    cur = wechat_db.cursor()
    cur.execute('''
        SELECT schedule, title
        FROM schedule
        WHERE accumulate_hours >= '{learned_hours}'
        ORDER BY accumulate_hours
        LIMIT 1
    '''.format(learned_hours=learned_hours))
    aim_lesson = ' '.join(cur.fetchone())
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


def update_schedule(is_update):
    if is_update:
        cur = info_db.cursor()
        cur_wechat = wechat_db.cursor()
        cur_wechat.execute('TRUNCATE TABLE schedule')
        for course_id in courses:
            cur.execute('''
                SELECT chapter.seq, lesson.seq, chapter.title, lesson.title, lesson.hour
                FROM school_chapter chapter
                LEFT JOIN school_lesson lesson
                ON chapter.id = lesson.chapter_id
                WHERE chapter.course_id = '{course_id}'
                ORDER BY chapter.seq, lesson.seq
            '''.format(course_id=course_id))
            accumulate_hours = 0
            for row in cur:
                accumulate_hours += row[-1]
                _update_db(course_id, accumulate_hours, row)


def _update_db(course_id, accumulate_hours, row):
    chapter_id, lesson_id, chapter_title, lesson_title, _ = row
    schedule = '%s-%s' % (chapter_id, lesson_id)
    title = '%s-%s' % (chapter_title, lesson_title)
    values = "%s, '%s', '%s', %s" % (course_id, schedule, title, accumulate_hours)
    data_save('schedule', values)
    # cur = wechat_db.cursor()
    # cur.execute('''
    #     INSERT INTO schedule
    #     ('course_id, schedule, title, hours')
    #     SELECT '1', '22', '333', '1'
    #     FROM dual
    #     WHERE NOT EXISTS
    #     (SELECT * FROM schedule
    #     WHERE schedule.title='aaa')
    # ''')


def run(is_update_schedule=False):
    """
    search_students_info -> search_wechat -> comb_info -> send_msg
    """
    update_schedule(is_update_schedule)
    for course_id in courses:
        whole_hours = _get_whole_hours(course_id)
        students_info = search_students_info(course_id)
        for stu_info in students_info:
            wechat_id = search_wechat_id(stu_info[:2])
            if wechat_id:
                msg = comb_info(wechat_id, whole_hours, stu_info)
                send_msg(wechat_id, msg)

if __name__ == '__main__':
    run()
