#!/usr/local/bin/python3.5
from matplotlib import pyplot as plt
import openpyxl
import pymysql
from pylab import mpl
db = pymysql.connect('23.83.235.63', 'markdev', 'mark2017', 'codeclass', charset="utf8")
cur = db.cursor()

mpl.rcParams['font.sans-serif'] = ['FangSong']      # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False           # 解决保存图像是负号'-'显示为方块的问题


def get_members(file='members.xlsx'):
    """
    从成员信息文件获取并返回全体成员用户名生成器
    """
    wb = openpyxl.load_workbook(file)
    ws = wb.active
    for row in ws:
        if row[0]:
            yield row[0].value
        else:
            yield row[1].value


def _get_data(username):
    """
    从数据库获取并返回当前学员进度信息
    """
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
     ;'''.format(username=username))
    return cur.fetchone()


def get_process(file='members.xlsx'):
    """
     获取全体学员进度信息，已知学员、未知学员
    """
    process = []
    total = []
    members = []
    missing = []
    for m in get_members(file):
        data = _get_data(m)
        if data:
            process.append(data[0])
            total.append(data[1])
            members.append(m)
        else:
            missing.append(m)
    return process, total, members, missing


def plot_process(process, limit):
    """
    课程进度散点图
    """
    plt.title('课程进度统计')
    process.sort()
    plt.plot(process, 'bo')
    plt.axhline(limit, color='r')


def plot_total(total, limit):
    """
    课程总数散点图
    """
    plt.title('课程总数统计')
    total.sort()
    plt.plot(total, 'gs')
    plt.axhline(limit, color='r')


def plot_members(members, missing):
    """
    成员信息饼状图
    """
    plt.title('成员统计')
    x = (len(members), len(missing))
    explode = (0, 0.1)
    labels = ('已统计人数%d' % x[0], '未统计人数%d' % x[1])
    autopct = '%3.1f%%'
    startangle = 90
    plt.pie(x, explode, labels, autopct=autopct, startangle=startangle)


def run(process_limit, total_limit, filename='members.xlsx', img='statistic.png'):
    process, total, members, missing = get_process(filename)
    plt.subplot(221)
    plot_process(process, process_limit)
    plt.subplot(222)
    plot_total(total, total_limit)
    plt.subplot(223)
    plot_members(members, missing)
    plt.savefig(img)
    plt.show()


if __name__ == '__main__':
    # members_file = input('请输入群成员文件名：')
    run(7, 40)
