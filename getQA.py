#!/usr/local/bin/python3.5
from functools import wraps
import pymysql
import datetime
# db = pymysql.connect('localhost', 'root', 'markdev2017', 'codeclass', charset="utf8")
db = pymysql.connect('localhost', 'markdev', 'mark2017', 'codeclass', charset="utf8")
# TODO 数据库结构修改
db_table_column = {
    'qa_question': 'create_time, checked',
    'qa_answer': 'answer, modify_time',
    'qa_description': 'description, question_id',
    'qa_answer_questions': 'answer_id, question_id'
}


def keep_contact(func):
    """
    装饰器，使数据库保持连接
    """
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        if not db.open:
            db.ping()
        func(*args, **kwargs)
    return wrapped_func


def data_save(table_name, values):
    """
    数据库接口
     table_name：表名
     value：
    """
    cur = db.cursor()
    cur.execute('INSERT INTO {} ({}) VALUES ({})'.format(
        table_name,
        db_table_column[table_name],
        values
    ))
    cur.execute('SELECT LAST_INSERT_ID()')
    new_id = cur.fetchone()[0]
    db.commit()
    return new_id


@keep_contact
def save_question():
    """
    接受传入的问题，存入数据库
    """
    values = '"{}", False'.format(datetime.datetime.now())
    print('save_question', values)
    question_id = data_save('qa_question', values)
    return question_id


@keep_contact
def save_answer(msg, qid):
    """
    接收传入的答案，存入数据库
    """
    values = '{}, "{}"'.format(msg, datetime.datetime.now())
    answer_id = data_save('qa_answer', values)
    ids = '{}, {}'.format(answer_id, qid)
    data_save('qa_answer_questions', ids)
    # return answer_id


@keep_contact
def save_desc(msg, qid):
    """
    存储新问题，返回 id
    """
    values = '{}, {}'.format(msg, qid)
    desc_id = data_save('qa_description', values)
    # return desc_id
