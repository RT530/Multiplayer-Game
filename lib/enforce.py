from functools import wraps
from time import sleep


def enforce(redo=None, sleep_time=0):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if redo is None:
                while True:
                    try:
                        return func(*args, **kwargs)
                    except:
                        sleep(sleep_time)
            else:
                for i in range(redo-1):
                    try:
                        return func(*args, **kwargs)
                    except:
                        sleep(sleep_time)
                return func(*args, **kwargs)

        return wrapper

    return decorate
