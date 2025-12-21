import time
from typing import Generator

# 1. 가상의 로그 데이터를 생성하는 제너레이터 (파일 대신 사용 가능)
def mock_log_generator(count):
    for i in range(count):
        level = "ERROR" if i % 5 == 0 else "INFO"
        yield f"2025-12-21 16:00:{i:02d} | {level} | Message number {i} | UserID: {i+100}"

def log_filter(log_stream: Generator[str, None, None]):
    for log in log_stream:
        if log.find("ERROR") >= 0:
            yield log

def log_parser(log_stream: Generator[str, None, None]):
    for log in log_stream:
        log_split = log.split(" | ")
        yield (log_split[0], log_split[2])

# 실행 예시
log_stream = mock_log_generator(10000000000000000000000)
filtered = log_filter(log_stream)
parsed = log_parser(filtered)

for timestamp, message in parsed:
    print(f"[{timestamp}] {message}")