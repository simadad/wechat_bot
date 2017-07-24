import itchat
import datetime
import os
from statistic import db
from matplotlib import pyplot as plt
from personal_plan import log_this
from processor import friend_mark

# thistime = datetime.datetime.now()
thistime = datetime.datetime.strptime('2017-05-10', '%Y-%m-%d')
gap_day = 7
gap_hour = 6
gap_day_label = ['一', '二', '三', '四', '五', '六', '日']
# gap_hour_label = ['子-卯', '卯-午', '午-酉', '酉-子']
gap_hour_label = ['凌晨', '上午', '下午', '晚上']
x_label = '星期'
# y_label = '时辰'
y_label = '时段'
title = '上周课程活力统计图'
itchat.auto_login(hotReload=True)
log_path = 'log/log_graphs'

graph_dir = 'graphs'
graph_send_dir = 'send'
groups = ['20170424', ]


@log_this
def get_members(name: str):
    """
    根据群名称，返回群ID、群成员生成器
    """
    print('group name: ', name)
    room = itchat.search_chatrooms(name=name)[0]
    print('username: ', room['UserName'])
    # nickname = rooms[0]['NickName']
    # print(username)
    # yield name, nickname, username
    # yield username
    # room_info = itchat.update_chatroom(userName=username)
    members_info = room.update()['MemberList']
    print('members_info-len: ', len(members_info))
    for m in members_info:
        # print(m)
        # if m['DisplayName']:
        #     yield m['DisplayName']
        # else:
        #     yield m['NickName']
        print('member[nickname]: ', m['NickName'])
        yield m['NickName'].lstrip(friend_mark['lab'])


@log_this
def get_time(members, gap=gap_day):
    """
    接收群成员，统计时间区间（默认最近7天），返回时间序列生成器
    """
    cur = db.cursor()
    now = thistime.strftime('%Y-%m-%d %H:%M:%S')
    for username in members:
        cur.execute('''
        SELECT learned.learn_time
        FROM school_learnedlesson learned
        LEFT JOIN auth_user user
        ON user.id = learned.user_id
        WHERE datediff('{now}', learned.learn_time) >= 0
        AND datediff('{now}', learned.learn_time) < {gap}
        AND user.username = '{username}'
        '''.format(username=username, gap=gap, now=now))
        print('username: ', username)
        print('now: ', now)
        for time in cur:
            print('time_msq: ', time)
            yield time[0]


@log_this
def get_data(all_time):
    """
    组合二维时间序列
    :return:
    """
    data = [[0 for _ in range(gap_day)] for __ in range(int(24 / gap_hour))]
    for time in all_time:
        print('time: ', time)
        days = (thistime.date() - time.date()).days
        print('days: ', days)
        hours = time.hour // gap_hour
        print('hours: ', hours)
        data[hours][days] += 1
    return data


@log_this
def make_graph(name, data):
    # data = [[1, 0, 3, 5, 2, 1, 6],
    #          [7, 3, 1, 7, 3, 5, 8],
    #          [2, 3, 4, 5, 2, 1, 6],
    #          [1, 6, 2, 3, 6, 5, 4]]
    fig, ax = plt.subplots()
    im = ax.imshow(data, plt.cm.summer_r)
    plt.colorbar(im)
    ax.set_title(title, size=18)
    ax.set_xticks(range(gap_day))
    for i in range(gap_day):
        plt.axvline(x=i+0.5, color='black')
    ax.set_xticklabels(gap_day_label)
    ax.set_yticks(range(int(24/gap_hour)))
    for j in range(int(24/gap_hour)):
        plt.axhline(y=j+0.5, color='black')
    ax.set_yticklabels(gap_hour_label)
    ax.set_ylabel(y_label, size=15)
    ax.set_xlabel(x_label, size=15)
    # plt.show()
    graph_name = graph_dir + '/' + name + '/' + thistime.strftime('%Y-%m-%d') + '.png'
    try:
        plt.savefig(graph_name)
    except FileNotFoundError:
        os.mkdir(graph_dir+'/'+name)
        plt.savefig(graph_name)
    with open(log_path, 'a', encoding='utf8') as f:
        f.write('{time:<30}\n{graph:<30}SAVED!\n'.format(time=thistime, graph=graph_name))
    return graph_name


def run():
    print('RUN: graph.py')
    for name in groups:
        # 获取成员
        members = get_members(name)
        # next(members)
        all_time = get_time(members)
        data = get_data(all_time)
        print('data: ', data)
        make_graph(name, data)

if __name__ == '__main__':
    run()
