import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from mybot import *

my_sender = '970373350@qq.com'  # 发件人邮箱账号
my_pass = 'eobtzbrbykhhbcac'  # 发件人邮箱密码
my_user = '970373350@qq.com'  # 收件人邮箱账号，我这边发送给自己

msg_model = '''
    <h1>断线重连</h1>
    <p><span>上次检测成功时间：</span>{last_time}</p>
    <p><span>本次图片生成时间：</span>{now_time}</p>
    <p><a href="http://lab.crossincode.com:8000/">Crossin实战训练营</a></p>
    <p><img src="cid:image1"></p>
'''


def mail_it(now):
    msg_root = MIMEMultipart('related')
    msg_alternative = MIMEMultipart('alternative')
    with open('QR.png', 'rb') as f:
        msg_image = MIMEImage(f.read())
    with open('check_time_list', encoding='utf8') as f:
        last_time = f.read()
    msg_content = msg_model.format(last_time=last_time, now_time=now)
    msg_image.add_header('Content-ID', '<image1>')
    msg_alternative.attach(MIMEText(msg_content, 'html', 'utf-8'))
    msg_root.attach(msg_alternative)
    msg_root.attach(msg_image)
    msg_root['From'] = formataddr(["助教·AI", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg_root['To'] = formataddr(["Crossin", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg_root['Subject'] = "断线重连"  # 邮件的主题，也可以说是标题

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
    server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(my_sender, [my_user, ], msg_root.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接


@itchat.msg_register(itchat.content.NOTE)
def note(info):
    print(info)


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text(info):
    print(info)
    itchat.send('aaa', info['FromUserName'])


def check_it():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reply_code = itchat.check_login()
    print('reply_code: ', reply_code)
    if reply_code != '200':
        itchat.get_QRuuid()
        itchat.get_QR(picDir='QR.png')
        mail_it(now)
        times = 0
        while itchat.check_login() != '200':
            times += 1
            print('fail\t%s' % times)
        print('web_init')
        itchat.web_init()
        print('show_mobile_login')
        itchat.show_mobile_login()
        print('get_contact')
        itchat.get_contact(True)
        print('start_receiving')
        itchat.start_receiving()
        print('run')
        itchat.run()
    else:
        with open('check_time_list', 'w', encoding='utf8') as f:
            f.write(now)


def login(**info):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    qrcode = info['qrcode']
    uuid = info['uuid']
    status = info['status']
    with open('QQQ.png', 'wb') as f:
        f.write(qrcode)
    mail_it(now)


def check():
    code = itchat.check_login()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if code != '200':
        itchat.auto_login()
        mail_it(now)
        itchat.run()

if __name__ == '__main__':
    check_it()
    # print('200')
    # print(11111)
    # itchat.get_QRuuid()
    # print(2222222)
    # itchat.get_QR()
    # while itchat.check_login() != '200':
    #     print(333333333)
    # itchat.web_init()
    # print(4444444)
    # itchat.show_mobile_login()
    # print(555555555)
    # itchat.get_contact(True)
    # print(666666666666)
    # itchat.start_receiving()
    # # itchat.run()
    # # itchat.auto_login(qrCallback=login)
    # # itchat.auto_login()
    # print(7777777777)
    # itchat.run()
    # print(99999999999)
