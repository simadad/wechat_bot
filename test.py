# coding: UTF-8
# filename: moniter.py

import time
import requests
import bs4

url = 'http://www.caorongduan.com/index.php/archives/3/'
last_modified = ''


def get_page():
    global last_modified
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
        'Connection': 'keep-alive'
    }
    if last_modified:
        headers['If-Modified-Since'] = last_modified
    res = requests.get(url, headers=headers)
    for i in res.headers:
        print i
    if res.status_code == 200:
        if last_modified and last_modified is not res.headers['Last-Modified']:
            print 'page has changed\r',
            return False
        # last_modified = res.headers['Last-Modified']
    elif res.status_code == 304:
        print 'normal\r',
    return True
#
# if __name__ == '__main__':
#     while 1:
#         result = get_page()
#         if result:
#             time.sleep(2)
#         else:
#             break

s = '<div class="aa" id="bb">asdasd</div>'
soup = bs4.BeautifulSoup(s, "html.parser")
print soup.text
print soup
print soup.div['id']
# print soup['id']
