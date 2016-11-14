# -*- coding: utf-8 -*
import logging


def execute(db, sql):
    from django.db import connections, transaction
    cursor = connections[db].cursor()  # 获得一个游标(cursor)对象
    # 查询操作
    result = dict()
    cursor.execute(sql)
    desc = cursor.description
    raw = cursor.fetchone()  # 返回结果行 或使用 #raw = cursor.fetchall()
    for tu in desc:
        index = desc.index(tu)
        result[tu[0]] = raw[index]
    return result
