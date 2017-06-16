import itchat
import datetime
from statistic import db
from matplotlib import pyplot as plt

# thistime = datetime.datetime.now()
thistime = datetime.datetime.strptime('2017-05-20', '%Y-%m-%d')
gap_day = 7
gap_hour = 6
gap_day_label = ['一', '二', '三', '四', '五', '六', '日']
# gap_hour_label = ['子-卯', '卯-午', '午-酉', '酉-子']
gap_hour_label = ['凌晨', '上午', '下午', '晚上']
x_label = '星期'
# y_label = '时辰'
y_label = '时段'
title = '上周课程活力统计图'
data = [[0 for _ in range(gap_day)] for __ in range(int(24/gap_hour))]
itchat.auto_login(hotReload=True)


def get_members(name: str):
    """
    根据群名称，返回群ID、群成员生成器
    """
    rooms = itchat.search_chatrooms(name=name)
    username = rooms[0]['UserName']
    # nickname = rooms[0]['NickName']
    # print(username)
    # yield name, nickname, username
    yield username
    room_info = itchat.update_chatroom(userName=username)
    members_info = room_info['MemberList']
    for m in members_info:
        if m['DisplayName']:
            yield m['DisplayName']
        else:
            yield m['NickName']


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
        WHERE datediff('{now}', learned.learn_time) < {gap}
        AND user.username = '{username}'
        '''.format(username=username, gap=gap, now=now))
        for time in cur:
            yield time[0]


def split_time(time: datetime.datetime):
    days = (thistime - time).days
    hours = time.hour//gap_hour
    data[hours][days] += 1


def make_graph(datas):
    datas = [[1, 0, 3, 5, 2, 1, 6],
             [7, 3, 1, 7, 3, 5, 8],
             [2, 3, 4, 5, 2, 1, 6],
             [1, 6, 2, 3, 6, 5, 4]]
    fig, ax = plt.subplots()
    im = ax.imshow(datas, plt.cm.summer_r)
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
    graph_name = thistime.strftime('%Y-%m-%d') + '.png'
    plt.savefig(graph_name)
    return graph_name


def test_group(name):
    rooms = itchat.search_chatrooms(name=name)
    username = rooms[0]['UserName']
    return username


def run(name='20170424'):
    members = get_members(name)
    username = next(members)
    all_time = get_time(members)
    for time in all_time:
        split_time(time)
    img = make_graph(data)
    username = test_group('B')      # todo del
    itchat.send('@img@%s' % img, username)

if __name__ == '__main__':
    run()
