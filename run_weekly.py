import itchat
import os
import shutil
import datetime
from personal_plan import log_this
from graph import graph_dir, graph_send_dir, log_path

itchat.auto_login(hotReload=True)
test_name = 'B'


def test_group():
    rooms = itchat.search_chatrooms(name=test_name)
    username = rooms[0]['UserName']
    return username


@log_this
def send_graph():
    cwd = os.getcwd()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    root_dir = cwd + '/' + graph_dir
    with open(log_path, 'a', encoding='utf8') as f:
        f.write('\n{now}:\n'.format(now=now))
        for name in os.listdir(root_dir):
            rooms = itchat.search_chatrooms(name=name)
            username = rooms[0]['UserName']
            name_dir = root_dir + '/' + name
            for file in os.listdir(name_dir):
                img_path = name_dir + '/' + file
                if os.path.isfile(img_path):
                    username = test_group()             # TODO del
                    itchat.send('@img@%s' % img_path, username)
                    f.write('{img:<20}SEND!\n'.format(img=file))
                    send_dir = name_dir + '/' + graph_send_dir + '/' + file
                    try:
                        shutil.move(img_path, send_dir)
                    except FileNotFoundError:
                        os.mkdir(name_dir + '/' + graph_send_dir)
                        shutil.move(img_path, send_dir)
                    f.write('{img:<20}MOVED!\n'.format(img=file))
        f.write('\n')


def run():
    send_graph()

if __name__ == '__main__':
    run()
