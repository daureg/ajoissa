#! /usr/bin/python
# vim: set fileencoding=utf-8
"""Return task name or create new one."""
import sys
import re
import string
from datetime import datetime
from dateutil.parser import parse as parse_date
from tzlocal import get_localzone
from pytz import UTC


# first result from Google: http://hetland.org/coding/python/levenshtein.py
def _levenshtein(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n+1)
    for i in range(1, m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1, n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def alternatives(l):
    """Display numbered l until user make a valid choice"""
    if len(l) == 1:
        return 0
    prompt = '\n'.join(['[{}]: {}'.format(i, v) for i, v in enumerate(l)])
    selection = -1
    while (not (0 <= selection < len(l))):
        print(prompt)
        choice = input()
        # either numerically
        try:
            selection = int(choice)
        except ValueError:
            # or by a unambiguous prefix
            candidate = [(t, i) for i, t in enumerate(l)
                         if t.startswith(choice)]
            if len(candidate) == 1:
                return candidate[0][1]
    return selection


def find_task(req, tasks):
    """Find closest task to req or create a new one"""
    req = req.lower()
    if req == '_':
        return None
    if req in tasks:
        return req
    candidate = [t for t in tasks if t.startswith(req)]
    if len(candidate) == 1:
        return candidate[0]
    if len(candidate) > 1:
        return candidate[alternatives(candidate)]
    distance = sorted([(t, _levenshtein(t, req)) for t in tasks],
                      key=lambda x: x[1])
    candidate = [req+' (create)'] + [t[0] for t in distance]
    choice = alternatives(candidate)
    if choice == 0:
        # tasks.append(req)
        return req
    return candidate[choice]


def get_time_period(s):
    if s is None:
        return None
    numbers = len([c for c in s if c in string.digits])
    if numbers < 0.5*len(s):
        print(s + ' is probably not a date, not enough number')
        return None
    parts = re.split(r'[-_/]+', s)
    if len(parts) != 2:
        print(s + ' does not split well')
        return None
    #TODO use day of [0] as default in [1]
    #TODO ensure that [0] < [1]
    return read_date(parts[0]), read_date(parts[1])


def read_date(s):
    default = datetime.now()
    default = default.replace(minute=0, second=0, microsecond=0)
    if default.hour <= 4:
        default = default.replace(day=default.day-1)
    try:
        return get_localzone().localize(parse_date(s, dayfirst=True,
                                                   default=default),
                                        is_dst=True).astimezone(UTC)
    except TypeError:
        print(s + ' does not look like a date')
        return None


def parse_task(tasks, args):
    req = '' if len(args) <= 1 else args[1]
    second = None if len(args) <= 2 else args[2]
    period = get_time_period(second)
    third = None if len(args) <= 3 else args[3]
    if period is None:
        comment = second
        period = get_time_period(third)
    else:
        comment = third
    if period is None:
        period = (datetime.utcnow(), None)

    task = find_task(req, tasks)
    return (task, comment, period)

if __name__ == '__main__':
    tasks = ['finnish', 'monde', 'bio', 'bold']
    print(parse_task(tasks, sys.argv))
