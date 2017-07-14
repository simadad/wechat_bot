#!/usr/local/bin/python3.5
import itchat
import datetime
import json
from functools import wraps
from statistic import db as info_db
from getQA import db as wechat_db
from getQA import db_table_column, data_save

db_table_column['user_wechat'] = 'username, wechat, new_wechat'
db_table_column['schedule'] = 'course_id, schedule, title, accumulate_hours'
remind_gap_week = (1, 2, 4, 8)       # 督促间隔
remind_gap = [x*7 for x in remind_gap_week]
courses = ('1', '2')
max_chapter = {
    '1': 12,
    '2': 7
}
msg_model = {
    'base': 'etc/base',
    'model': 'etc/model.json',
    'urge': 'etc/urge',
    'confirm': 'etc/confirm'
}
log_path = {
    'log_msg': 'log/log_msg',
    'log_error': 'log/log_error',
    'log_missing': 'log/log_missing',
    'log_confirm': 'log/log_confirm',
}
judge = {
    '1': '<= 100',
    '2': '> 100'
}
confirm = {
            'total': 0,  # 总人数
            'missing': 0,  # 无微信
            'skip_r': 0,  # 非当日督促
            'skip_rp': 0,  # 非当日提醒
            'lack': 0,  # 缺失信息
            'finished': 0,  # 已完结
            'skip': 0,  # 总未推送人次
            'send': 0,  # 推送人次
        }
now = datetime.datetime.now().date() + datetime.timedelta(days=0)
itchat.auto_login(hotReload=True)


def log_this(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return result
        except Exception as e:
            log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # func = 'Function: %s' % f.__name__
            para = 'args: {args}\n kwargs: {kwargs}'.format(args=args, kwargs=kwargs)
            # error = 'Error: %s' % e
            log = '{log_time}\n{func}\n{para}\n{error}\n{cut:-<40}\n\n'.format(
                log_time=log_time, func=f.__name__, para=para, error=e, cut=''
            )
            with open(log_path['log_error'], 'a', encoding='utf8') as file:
                file.write(log)
    return wrapper


@log_this
def search_students_info(course_id):
    """
    搜索并返回符合条件的信息生成器
    网站用户名-微信号-推送频率-计划起始日-计划到期日-总课时
    :return:
    """
    cur = info_db.cursor()
    cur.execute('''
    SELECT user.username, bill.wechat, vip.remind, vip.remind_plan, vip.remind_days,
    user.last_login, MAX(chapter.seq), plan.start_date, plan.end_date, SUM(lesson.hour)
    FROM school_learnedlesson learned
    JOIN school_lesson lesson
    ON lesson.id = learned.lesson_id
    JOIN school_chapter chapter
    ON chapter.id = lesson.chapter_id
    JOIN auth_user user
    ON user.id = learned.user_id
    JOIN school_plan plan
    ON user.id = plan.user_id
    JOIN vip_premium vip
    ON user.id = vip.user_id
    JOIN vip_bill bill
    ON user.id = bill.vip_user_id
    WHERE plan.course_id = {course_id}
    AND learned.lesson_id {judge}
    GROUP BY user.username
    '''.format(course_id=course_id, judge=judge[course_id]))
    for row in cur:
        yield row


@log_this
def _to_remind(start_date, end_date, remind_days):
    """
    确认当天是否推送
    """
    if start_date and end_date is not None:
        days = (now - start_date).days
        if now <= end_date and days % remind_days == 0:
            return True
        confirm['skip_rp'] += 1
        return False
    confirm['lack'] += 1
    return False


@log_this
def _urge_weeks(course_id, present_chapter, last_login):
    """
    确定当天是否督促
    """
    # 如果当前章节小于最大章节
    if int(present_chapter) < max_chapter[course_id]:
        # 今日至最后登录时间之间隔天数
        gap = (now - last_login.date()).days
        # 如果间隔天数恰好为响应天数（1、2、4、8周）返回间隔周数
        if gap in remind_gap:
            return gap / 7
        confirm['skip_r'] += 1
        return False
    confirm['finished'] += 1
    return False


@log_this
def search_wechat_id(username, wechat):
    """
    接受username，返回微信最新UserName
    :return:
    """
    user = itchat.search_friends(wechat) or itchat.search_friends(username)
    if len(user) == 1:
        wechat_id = user[0]['UserName']
    else:
        wechat_id = _confirm(username, wechat)
    return wechat_id


@log_this
def _confirm(username, wechat):
    """
    本地数据库确认可用微信号
    :return:
    """
    log_time = now.strftime('%Y-%m-%d')
    if wechat is None:
        wechat = 'NoWeChat'
    log = '{time:<40}:\n{username:<20}{wechat:<20}\n{cut:-<40}\n\n'.format(
        time=log_time, username=username, wechat=wechat, cut=''
    )
    with open(log_path['log_missing'], 'a', encoding='utf8') as f:
        f.write(log)
    # print('missing: ', stu_info)
    # TODO 正确微信号确认
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


@log_this
def comb_info(username, course_id, info: tuple=False, weeks: int=False):
    """
    组合信息，返回消息模版
    """
    if info:
        whole_hours, start_date, end_date, learned_hours = info
        aim_lesson = _get_aim_lesson(course_id, whole_hours, learned_hours, end_date)
        model = _model_choice(whole_hours, start_date, end_date, learned_hours)
        # 调取模版返回消息
        msg = _get_msg(username, (aim_lesson, model))
    else:
        # 调取模版返回消息
        msg = _get_msg(username, weeks=weeks)
    return msg


@log_this
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
    hours = cur.fetchone()[0]
    return hours


@log_this
def _get_aim_lesson(course_id, whole_hours, learned_hours, end_date):
    """
    计算目标课程
    """
    days = (end_date - now).days + 1
    rest_hours = whole_hours - learned_hours
    if days < 0 or rest_hours < 0:
        learned_hours = whole_hours
    else:
        learned_hours += rest_hours / days
    cur = wechat_db.cursor()
    cur.execute('''
        SELECT schedule, title
        FROM schedule
        WHERE accumulate_hours >= '{learned_hours}'
        AND course_id = {course_id}
        ORDER BY accumulate_hours
        LIMIT 1
    '''.format(learned_hours=learned_hours, course_id=course_id))
    resule = cur.fetchone()
    aim_lesson = ' '.join(resule)
    return aim_lesson


@log_this
def _model_choice(whole_hours, start_date, end_date, learned_hours):
    """
    选择消息模版
    """
    whole_days = (end_date - start_date).days + 1
    learned_days = (now - start_date).days
    if learned_hours/whole_hours >= learned_days/whole_days:
        model = 'ahead'
    else:
        model = 'behind'
    return model


@log_this
def _get_msg(username, info: tuple=False, weeks: int=False):
    """
    组合消息
    """
    if info:
        aim_lesson, model = info
        with open(msg_model['base'], encoding='utf8') as f:
            base_msg = f.read()
        with open(msg_model['model'], encoding='utf8') as f:
            text = json.load(f)
            tips = text[model]
        msg = base_msg.format(username=username, aim_lesson=aim_lesson, tips=tips)
    else:
        with open(msg_model['urge'], encoding='utf8') as f:
            urge_msg = f.read()
        msg = urge_msg.format(username=username, week=weeks)
    return msg


@log_this
def send_msg(wechat_id, msg, stu_info):
    """
    发送消息
    :return:
    """
    msg = wechat_id + ':\n' + msg
    room = itchat.search_chatrooms('B')
    room_id = room[0]['UserName']
    # itchat.send(msg, wechat_id)
    # print(msg, username)
    itchat.send(msg, room_id)            # TODO del #
    confirm['send'] += 1
    username, wechat = stu_info
    if wechat is None:
        wechat = 'None'
    log_time = now.strftime('%Y-%m-%d')
    with open(log_path['log_msg'], 'a', encoding='utf8') as f:
        log = '{username:<20}{wechat:<20}{log_time:<20}:\n{msg}\n{cut:-<60}\n\n'.format(
            username=username, wechat=wechat, log_time=log_time, msg=msg, cut=''
        )
        f.write(log)


@log_this
def update_schedule(is_update):
    """
    更新本地章节用时进度表
    """
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


@log_this
def _update_db(course_id, accumulate_hours, row):
    """
     更新本地数据库
    """
    chapter_id, lesson_id, chapter_title, lesson_title, _ = row
    schedule = '%s-%s' % (chapter_id, lesson_id)
    title = '%s-%s' % (chapter_title, lesson_title)
    values = "%s, '%s', '%s', %s" % (course_id, schedule, title, accumulate_hours)
    data_save('schedule', values)


def _confirm_log(course_id):
    """
    记录当次推送统计信息
    """
    with open(msg_model['confirm'], encoding='utf8') as f:
        confirm_msg = f.read()
    with open(log_path['log_confirm'], 'a', encoding='utf8') as f:
        total_record = confirm['total']
        missing = confirm['missing']
        send = confirm['send']
        skip = confirm['skip']
        total_sum = missing + send + skip
        f.write(confirm_msg.format(
            finished=confirm['finished'], skip_r=confirm['skip_r'], lack=confirm['lack'],
            missing=confirm['missing'], send=confirm['send'], skip=confirm['skip'], skip_rp=confirm['skip_rp'],
            log_time=str(now), total=confirm['total'], right=total_record == total_sum, course=course_id
        ))


@log_this
def remind_it(username, wechat, course_id, info: tuple=False, weeks: int=False):
    """
    推送消息
    """
    # 获取用户 itchat  UserName
    wechat_id = search_wechat_id(username, wechat)
    if info:
        whole_hours, start_date, end_date, learned_hours = info
        msg = comb_info(username, course_id, (whole_hours, start_date, end_date, learned_hours))
    else:
        msg = comb_info(username, course_id, weeks=weeks)
    if wechat_id:
        send_msg(wechat_id, msg, (username, wechat))
    else:
        confirm['missing'] += 1


# @log_this
def run(is_update_schedule=False):
    """
    search_students_info -> search_wechat -> comb_info -> send_msg
    """
    # 更新本地数据库章节用时信息
    update_schedule(is_update_schedule)
    # 循环每一课程（基础/爬虫）
    for course_id in courses:
        # 获取课程总课时
        whole_hours = _get_whole_hours(course_id)
        # 获取本课程所有学生信息生成器
        students_info = search_students_info(course_id)
        for stu_info in students_info:
            confirm['total'] += 1
            username, wechat, remind, remind_plan, remind_days, last_login, \
                present_chapter, start_date, end_date, learned_hours = stu_info
            # 如果设定督促，且今天为督促日，发送督促信息
            if remind and _urge_weeks(course_id, present_chapter, last_login):
                weeks = _urge_weeks(course_id, present_chapter, last_login)
                remind_it(username, wechat, course_id, weeks=int(weeks))
            # 如果设定定时推送，且今天为推送日，发送推送信息
            elif remind_plan and _to_remind(start_date, end_date, remind_days):
                remind_it(username, wechat, course_id, (whole_hours, start_date, end_date, learned_hours))
            elif not remind and not remind_plan:
                confirm['finished'] += 1
            else:
                confirm['skip'] += 1
        _confirm_log(course_id)


if __name__ == '__main__':
    run()
