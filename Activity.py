# vim: set fileencoding=utf-8
import app_specific
import time


def get_time_offset(t):
    """
    Given a local time, return the floating number of hours that one needs to
    add to UTC time to get the original one back. For instance, in France
    during summer:
    UTC:    20:50
    local:  22:50
    return: 2.0
    """
    if hasattr(t, 'tm_gmtoff'):
        return t.tm_gmtoff/3600.0

    is_dst = time.daylight and t.tm_isdst > 0
    return - (time.altzone if is_dst else time.timezone)/3600.0


def make_sleep_activity(machine, start_time, start_tz, start_ip, end_time,
                        end_tz, end_ip):
    a = Activity(start_ip, machine, "sleep", "OS")
    a.start = start_time
    a.start_tz = start_tz
    a.end = end_time
    a.end_tz = end_tz
    a.end_ip = end_ip
    return a


class Activity():
    """Describe the lifetime of a specific application used on a specific
    document."""
    def __init__(self, ip, machine, title, app=None):
        self.start = int(time.time())
        self.start_tz = get_time_offset(time.localtime())
        self.start_ip = ip
        self.end = self.start
        self.end_tz = self.start_tz
        self.end_ip = self.start_ip
        self.machine = machine
        if app is None:  # probably windows, maybe try GetProcessImageFileName
            s = title.split(' - ')
            if len(s) > 1:
                title = s[:-1]
                app = s[-1]
            else:
                # not sure here. It may be that there is only the app name,
                # like "SpeedFan 4.49", only a title "Choose a file…" or both,
                # but with a different separator than "title - app". These
                # cases should be logged somewhere (in another table ? but is
                # it the responsibility of the class Activity?)
                app = "UNKNOWN"
        self.app = app.lower()
        if hasattr(app_specific, app):
            title, tags, uri = getattr(app_specific, app)(title)
        else:
            tags = None
            uri = None
        self.title = title
        self._tags = None if tags is None else set(tags.lower().split(';'))
        self.uri = None if uri is None else uri.lower()

    def __eq__(self, other):
        return self.machine == other.machine and \
            self.app == other.app and \
            self.title.lower() == other.title.lower() and \
            self.tags == other.tags and \
            self.uri == other.uri

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def tags(self):
        """';' separated list of tags describing the activity."""
        if self._tags is None:
            return None
        return ';'.join(list(self._tags))

    def build_insertion_tuple(self, ip):
        self.end = int(time.time())
        self.end_tz = get_time_offset(time.localtime())
        self.end_ip = ip
        return self.insertion_tuple()

    def insertion_tuple(self):
        return (self.start, self.start_tz, self.start_ip, self.end,
                self.end_tz, self.end_ip, self.app, self.title,
                self.tags, self.uri, self.machine)

    def __str__(self):
        return str(self.insertion_tuple())

if __name__ == "__main__":
    import doctest
    doctest.testmod()
