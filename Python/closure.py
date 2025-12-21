def make_logger(service_name):    
    def logger(message):
        print(f"[{service_name}] {message}")
        
    return logger

# 클로저 생성
auth_logger = make_logger("AUTH-SERVICE")
order_logger = make_logger("ORDER-SERVICE")

# 외부 함수인 make_logger는 이미 실행이 종료되었지만,
# 반환된 auth_logger는 "AUTH-SERVICE"라는 값을 기억하고 있습니다.
auth_logger("로그인 성공")
order_logger("주문 생성됨")

# auth_logger가 기억하고 있는 '환경' 들여다보기
print(auth_logger.__closure__[0].cell_contents)

def counter():
    count = 0
    def increment():
        nonlocal count # 외부 함수의 count를 쓰겠다고 명시
        count += 1
        return count
    return increment

c = counter()
print(c()) # 1
print(c()) # 2


class Calc:
    def __init__(self):
        self._total = 0
    
    def plus(self, num: int):
        self._total += num
        return self._total

calc = Calc()
calc.plus(10)


def make_accumulator():
    total = 0
    def accumulate(num: int):
        nonlocal total
        total += num
        return total
    return accumulate

calc = make_accumulator()

print(calc(10))
print(calc(20))
print(calc(5))

def make_tag_wrapper(tag_name: str):
    cnt = 0
    def wrapper(string: str):
        nonlocal cnt
        cnt += 1
        print(f"[{tag_name}] 태그 사용 횟수: {cnt}")
        return f"<{tag_name}>{string}</{tag_name}>"
    return wrapper

tag_wrapper = make_tag_wrapper("strong")
print(tag_wrapper("hello!"))
print(tag_wrapper.__closure__[1].cell_contents)


texts = ["hello", "this is", "closure"]
list(map(tag_wrapper, texts))
