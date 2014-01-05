#! /usr/bin/python2
# vim: set fileencoding=utf-8
from DBStore import db_filepath, get_data_saving_path
from displayYast import get_project_list
from tasks import parse_task
from importYast import entry_generator
from tzlocal import get_localzone
from datetime import datetime
from persistent import save_var, load_var
from os.path import join as mk_path
import os
import sys
import sqlite3


def date_offset(dt):
    tz = get_localzone()
    return int(tz.utcoffset(datetime(dt.year, dt.month, dt.day,
                                     dt.hour)).total_seconds())


def make_task(parsed_arg, tasks):
    task, comment, period = parsed_arg
    if task is None:
        return None
    offset = date_offset(period[0])
    task = {'project': tasks.keys()[tasks.values().index(task)], 'start':
            period[0], 's_offset': offset, 'com': comment, 'end': None,
            'e_offset': None}
    if period[1] is not None:
        task.update({'end': period[1], 'e_offset': offset})
    return task


def insert_task(conn, task):
    query = """insert into entry(project, start_time, start_offset,
    stop_time, stop_offset, comments) values(?, ?, ?, ?, ?, ?)"""
    c = conn.cursor()
    c.execute(query, entry_generator([task]).next())
    c.close()


def insert_pending_task(conn, end, pending_file):
    try:
        pending_task = load_var(pending_file)
        pending_task['end'] = end
        pending_task['e_offset'] = date_offset(pending_task['end'])
        insert_task(conn, pending_task)
        os.remove(pending_file)
    except IOError:
        pass


def read_and_insert():
    db = db_filepath('laptop')
    end = datetime.utcnow()
    with sqlite3.connect(db) as conn:
        tasks = {id_: name.lower() for id_, name in
                 get_project_list(conn).items()}
        next_task = parse_task([x.lower() for x in tasks.values()], sys.argv)
        task = make_task(next_task, tasks)
        print(task)
        pending_file = mk_path(get_data_saving_path('tracker'), '_tsk')
        if task is None:
            insert_pending_task(conn, end, pending_file)
            return
        pending = task['end'] is None
        if pending:
            insert_pending_task(conn, end, pending_file)
            save_var(pending_file, task)
        else:
            insert_task(conn, task)

if __name__ == '__main__':
    read_and_insert()
