# print("input yout username: ", end="")
# user: str = input()

# print(f"Hi {user}!")

import time
from typing import Callable
from functools import wraps

def timer(ns: bool = False):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(func.__name__, "실행")
            start = time.perf_counter() if not ns else time.perf_counter_ns()
            result = func(*args, **kwargs)
            end = time.perf_counter() if not ns else time.perf_counter_ns()
            time_spent = end-start
            time_spent = f"{time_spent:.4f} second" if not ns else f"{time_spent} ns"
            print(f"[{func.__name__}] 실행 완료, 실행 시간: {time_spent}")
            return result
        return wrapper
    return decorator

@timer(ns=True)
def simp(s: str):
    print(s)

simp("simple")
print(simp.__name__)

@timer()
def simple_test(t):
    print(f"input is {t}.")

@timer()
def this_is_sparta(members: int, names: list):
    for name in names:
        print(f"'{name}': this is sparta!!!")

simple_test(2)

this_is_sparta(3, ["han", "dae", "kim"])

print(simple_test.__name__)