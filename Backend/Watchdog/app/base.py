import time
from abc import ABC, abstractmethod
from typing import Any, Protocol

try:
    from .models import Status, BaseCheckResult, BaseConfig, Message
except ImportError:
    from models import Status, BaseCheckResult, BaseConfig, Message


class BaseWatcher(ABC):
    def __init__(self, config: BaseConfig = BaseConfig(), max_retries: int = 3, backoff: int = 1) -> None:
        self.status = Status.normal
        self.config = config
        self.max_retries = max_retries
        self.backoff = backoff
        self.template = self.make_template()
    
    def signature(self) -> tuple[Any]:
        return tuple(sorted(self.config.model_dump().items()))

    def check(self) -> BaseCheckResult:
        try:
            for _ in range(self.max_retries):
                response = self.check_server()

                if response.status == Status.normal:
                    return response
                time.sleep(self.backoff)
            return response # type: ignore
        except:
            raise NotImplementedError
    
    @abstractmethod
    def check_server(self) -> BaseCheckResult:
        ...
    
    @abstractmethod
    def make_template(self) -> str:
        ...


class Notifier(Protocol):
    def send(self, msg: Message):
        ...
