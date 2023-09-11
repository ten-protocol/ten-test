import time


def timeit(function):
    """Decorator function to time a method call and return the time. """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        function(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time

    return wrapper