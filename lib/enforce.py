from functools import wraps


def enforce(func):
    """
        This function is for any program that I'm working on so it have so flexible
        This decorate will enforce the function to run until it success
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except:
                pass

    return wrapper
