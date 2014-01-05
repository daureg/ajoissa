#! /usr/bin/python2
# vim: set fileencoding=utf-8
import sqlite3
from datetime import datetime, timedelta
from itertools import groupby


def get_project_list(conn=None):
    if conn is None:
        conn = sqlite3.connect('yast.db')
    c = conn.cursor()
    return {id_: name for id_, name in c.execute('select * from project')}


def format_entry(e):
    res = {}
    res['project'] = e['project']
    s_offset = timedelta(seconds=e['start_offset'])
    start = datetime.strptime(e['start_time'], '%Y-%m-%d %H:%M:%S+00:00')
    res['start'] = start + s_offset
    stop = datetime.strptime(e['stop_time'], '%Y-%m-%d %H:%M:%S+00:00')
    e_offset = timedelta(seconds=e['stop_offset'])
    res['stop'] = stop + e_offset
    res['comment'] = e['comments']
    res['length'] = int((stop - start).total_seconds()/60)
    return res

if __name__ == '__main__':
    conn = sqlite3.connect('yast.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    projects = get_project_list()
    entries = []
    for e in list(c.execute('select * from entry order by start_time')):
        entries.append(format_entry(e))
    last = [x for x in entries if x['start'].year == 2013]
    for week, es in groupby(last, lambda x: x['start'].isocalendar()[1]):
        get_proj = lambda x: x['project']
        for proj, wpes in groupby(sorted(es, key=get_proj), get_proj):
            print('W{}:{}:{}'.format(week, projects[proj],
                                     sum([x['length'] for x in wpes])))
    a = sum([x['length'] for x in last])
    c.close()
    conn.close()
    print(a/60)
