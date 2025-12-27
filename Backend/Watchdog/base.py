import json
from abc import ABC, abstractmethod
from typing import Any, Protocol

try:
    from .models import Status, BaseCheckResult, BaseConfig
except ImportError:
    from models import Status, BaseCheckResult, BaseConfig


class BaseWatcher(ABC):
    def __init__(self, config: BaseConfig = BaseConfig(), max_retries: int = 3) -> None:
        self.status = Status.normal
        self.config = config
        self.max_retries = max_retries
    
    def signature(self) -> tuple[Any]:
        return tuple(sorted(self.config.model_dump().items()))

    def check(self) -> BaseCheckResult:
        try:
            for _ in range(self.max_retries):
                response = self.check_server()

                if response.status == Status.normal:
                    return response
            return response # type: ignore
        except:
            raise NotImplementedError
    
    @abstractmethod
    def check_server(self) -> BaseCheckResult:
        ...


class Notifier(Protocol):
    def send(self, msg: str):
        ...


def make_message_text(result: BaseCheckResult):
    data = result.model_dump(mode='json')
    return json.dumps(data, indent=2)