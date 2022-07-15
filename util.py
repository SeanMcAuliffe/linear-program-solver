from functools import wraps
from time import time
import sys


def timer(f):
    @wraps(f)
    def wrapper(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        sys.stderr.write(f"{f.__name__} took {te-ts:2.8} sec")
        return result
    return wrapper