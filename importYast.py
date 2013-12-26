#! /usr/bin/python2
# vim: set fileencoding=utf-8
"""Read a yast.com yearly report (cleaned HTML) and dump it into a sqlite db.
Change following parameters if needed:"""
YEAR = 2013
from pytz import timezone
TIMEZONE = timezone('Europe/Helsinki')  # or tzlocal.get_localzone()
# TIMEZONE = timezone('Europe/Paris')


import datetime
from persistent import save_var, load_var
import bs4
from bs4.element import Tag
PROJECT = {}
import pytz


def get_project_id(title):
    if title in PROJECT:
        return PROJECT[title]
    nid = len(PROJECT)
    PROJECT[title] = nid
    return nid


def read_table(t, title):
    t = t.find('tbody')
    entries = [x for x in t if isinstance(x, Tag) and x.name == 'tr']
    day = None
    month = None
    res = []
    project = get_project_id(title)
    for e in entries:
        r, month, day = read_entry(e, day, month)
        r['project'] = project
        res.append(r)
    return res


def read_group(g):
    title = g.find('div', class_='Header').find(class_='week').text.strip()
    entries = []
    children = [x for x in g.children
                if isinstance(x, Tag) and 'Header' not in x['class']]
    if len(children) == 1 and children[0].name == 'table':
        return read_table(children[0], title)
    for g in children:
        entries += read_group(g)
    return entries


def read_entry(e, day, month):
    tz = TIMEZONE
    res = {}
    try:
        _date = e.find(class_='date').text.split()[0]
        day, month = map(int, _date.split('.'))
    except IndexError:
        pass
    hour, mins = map(int, e.find(class_='timeSpan1').text.strip().split(':'))
    start = datetime.datetime(YEAR, month, day, hour, mins)
    res['start'] = tz.localize(start, is_dst=True).astimezone(pytz.utc)
    res['s_offset'] = int(tz.utcoffset(start, is_dst=True).total_seconds())
    hour, mins = map(int, e.find(class_='timeSpan2').text.strip().split(':'))
    if hour < start.hour:
        day += 1
    naive_end = datetime.datetime(YEAR, month, day, hour, mins)
    res['end'] = tz.localize(naive_end, is_dst=True).astimezone(pytz.utc)
    res['e_offset'] = int(tz.utcoffset(naive_end, is_dst=True).total_seconds())
    res['com'] = e.find(class_='comment').text.strip()
    return res, month, day


def entry_generator(entries):
    for e in entries:
        yield (e['project'], e['start'], e['s_offset'], e['end'],
               e['e_offset'], None if e['com'] == '' else e['com'])

if __name__ == '__main__':
    try:
        PROJECT = load_var('projects')
    except IOError:
        pass
    with open('tmp.html') as f:
        html = bs4.BeautifulSoup(f.read())
    body = html.find('body')
    groups = [g for g in body if g.name == 'div']
    entries = []
    for g in groups:
        entries += read_group(g)
    print(PROJECT)
    if len(PROJECT) > 1:
        save_var('projects', PROJECT)
    import sqlite3
    conn = sqlite3.connect('yast.db')
    c = conn.cursor()
    insert_project = 'insert or ignore into project(name, id) values(?, ?)'
    c.executemany(insert_project, PROJECT.items())
    conn.commit()
    insert_task = """insert into entry(project, start_time, start_offset,
    stop_time, stop_offset, comments) values(?, ?, ?, ?, ?, ?)"""
    c.executemany(insert_task, entry_generator(entries))
    conn.commit()
    c.close()
    conn.close()
