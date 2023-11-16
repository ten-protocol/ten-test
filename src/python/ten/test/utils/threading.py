import threading, re

REGEX = re.compile('Thread-(?P<num>\d$)', re.M)


def thread_num():
    """Return the thread number of the runner thread.

    If the main thread, this function will return 1, otherwise it will return the number of the
    runner thread as denoted by the name Thread-<num>.
    """
    name = threading.currentThread().getName()
    try:
        return int(REGEX.search(name).group('num'))
    except:
        return 1

