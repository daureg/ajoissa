# from https://github.com/takluyver/pyxdg/blob/master/xdg/BaseDirectory.py
import os
import re
import platform

if platform.system() == 'Windows':
    _home = os.environ.get('APP_DATA')
    default_data_home = os.path.join(_home, 'Local', 'share')
else:
    _home = os.path.expanduser('~')
    default_data_home = os.path.join(_home, '.local', 'share')

xdg_data_home = os.environ.get('XDG_DATA_HOME') or default_data_home


def find_db_name(prefix, dir_content):
    """Given the machine prefix and the content of a directory as list of
    string, it returns the last sequential filename following the template
    prefix_NNNNNN.db
    >>> find_db_name('laptop', [])
    'laptop_000000.db'
    >>> find_db_name('laptop', ['a.txt'])
    'laptop_000000.db'
    >>> find_db_name('laptop', ['a.txt', 'laptop32.db'])
    'laptop_000000.db'
    >>> find_db_name('laptop', ['a.txt', 'laptop_xor.db'])
    'laptop_000000.db'
    >>> find_db_name('laptop', ['a.txt', 'laptop_12.db'])
    'laptop_000012.db'
    >>> find_db_name('laptop', ['a.txt', 'laptop_12.db', 'laptop_122.db'])
    'laptop_000122.db'
    """
    template = re.compile(prefix + r'_(\d+)\.db')
    previous_number = []
    for filename in dir_content:
        match = template.search(filename)
        if match:
            previous_number.append(int(match.group(1)))

    if len(previous_number) == 0:
        next_number = 0
    else:
        next_number = max(list(previous_number))
    return prefix + '_{:06}.db'.format(next_number)


def get_data_saving_path(*resource):
    """Ensure ``$XDG_DATA_HOME/<resource>/`` exists, and return its path.
    'resource' should normally be the name of your application or a shared
    resource. Use this when saving or updating application data.
    """
    resource = os.path.join(*resource)
    assert not resource.startswith('/')
    path = os.path.join(xdg_data_home, resource)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def db_filepath(prefix):
    """ Wrap the two other functions."""
    folder = get_data_saving_path('tracker')
    return os.path.join(folder, find_db_name(prefix, os.listdir(folder)))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
