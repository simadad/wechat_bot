from functools import wraps
import pymysql
import datetime
db = pymysql.connect('localhost', 'root', 'xgh19920520', 'codeclass', charset="utf8")


def keep_contact(func):
    """
    装饰器，使数据库保持连接
    """
    @wraps(func)
    def wrapped_func(msg, *args, **kwargs):
        if not db.open:
            db.ping()
        func(msg)
    return wrapped_func


@keep_contact
def save_question(msg):
    """
    接受传入的问题，存入数据库
    """
    cur = db.cursor()
    cur.execute('''
    INSERT INTO qa_question (question, create_time, checked) \
    VALUES ('{}', '{}', False)
    '''.format(
        msg, datetime.datetime.now().strftime('%Y-%m-%d')
    ))
    db.commit()

'asdas{}'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
