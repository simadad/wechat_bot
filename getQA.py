from functools import wraps
import pymysql
import datetime
db = pymysql.connect('localhost', 'root', 'xgh19920520', 'codeclass', charset="utf8")
db_table_column = {
    'qa_question': ('question', 'create_time', 'checked'),
    'qa_answer': ('answer', 'modify_time'),
    'qa_answer_questions': ('answer_id', 'question_id')
}


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


def data_save(table_name, value):
    cur = db.cursor()
    cur.execute('''
    INSERT INTO {} ({}) VALUES ('{}', '{}', {})
    '''.format(
        table_name,
        ','.join(db_table_column[table_name]),
        value,
        datetime.datetime.now(),
        False
    ))
    cur.execute('SELECT LAST_INSERT_ID()')
    new_id = cur.fetchone()[0]
    db.commit()
    return new_id


@keep_contact
def save_question(msg):
    """
    接受传入的问题，存入数据库
    """
    question_id = data_save('qa_question', msg)
    return question_id


@keep_contact
def save_answer(msg):
    """
    接收传入的答案，存入数据库
    """
    answer_id = data_save('qa_answer', msg)
    return answer_id
