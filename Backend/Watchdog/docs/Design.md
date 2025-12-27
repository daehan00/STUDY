구현해야 하는 기능들:

- 서버 점검
- 비동기 처리
- 감시 대상 추가, 제거
- 알림 처리


### 서비스의 동작 흐름

1. 비동기 루프 -> 30초(변동)마다 작업 수행
    - 서비스가 죽지 않도록 주의


2. 관리중인 서버 목록 변동 감지
    - 모니터링 컨테이너에 목록을 전달해 줄 별도 컨테이너 구현
    - 모니터링 컨테이너는 내리지 않아도 변동사항을 유지할 수 있도록(목록 변경 시)
    - 모니터링 컨테이너에 이벤트 기반의 웹훅을 만들어서 트리거
    - 세마포어로 동시접근 제어


3. 신규 또는 제거 있으면 처리
    - 관리 서버들을 인스턴스화해서 관리.
    - 추가 또는 삭제 시 인스턴스 수정


4. 모든 서버로 헬스체크 전송
    - 프로토콜로 정의해서 전송 기능 작성.


5. 결과 감지 후 알림 전송
    - 결과 판단하는 함수 작성(헬스체크 결과 처리할 수 있도록)
    - 알림 전송 기능 작성


```python
import enum
from typing import Protocol
from abc import ABC, abstractmethod


MAX_RETRIES = 3

class Status(enum):
    normal: 0
    warning: 1
    critical: 2


class Watcher(ABC):
    def check() -> [tuple | None]:
        try:
            for _ in range(MAX_RETRIES):
                response = self.check_server()

                status, msg = self.parse(response)

                if not status.value:
                    return None
            return result
        except:
            raise UnExpectedError
    
    @abstractmethod
    def check_server() -> dict:
        ...
    
    @abstractmethod
    def parse(response: dict) -> tuple[Status, str]:
        ...


class Notifier(Protocol):
    def send(msg: str):
        ...


```



```python
import asyncio

async def server_change(servers: dict) -> dict:
    ...


check_sema = asyncio.Semaphore(5)
send_sema = asyncio.Semaphore(3)


async def check_alive(server) -> dict:
    async with check_sema:
        ...

async def send_alert(info: dict):
    async with send_sema:
        ...

async def main():
    server_changed = asyncio.Queue()
    servers = {}

    while True:
        # server_changed가 비었는지 검사하고 처리.
        if not queue.empty():
            servers = await serve_change(servers)


        for server in servers:
            info = check_alive(server)

            if info:
                send_alert(info)
    
asyncio.run(main())

```

