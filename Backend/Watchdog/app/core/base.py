import time
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Protocol

from app.core.models import Status, BaseCheckResult, BaseConfig, Message


class BaseWatcher(ABC):
    def __init__(self, config: BaseConfig = BaseConfig(), max_retries: int = 3, backoff: int = 1) -> None:
        self.status = Status.normal
        self.config = config
        self.max_retries = max_retries
        self.backoff = backoff
        self.template = self.make_template()
        self.sign = self._signature()
    
    def _signature(self) -> tuple[Any]:
        return tuple(sorted(self.config.model_dump().items()))

    @abstractmethod
    def _check_result(self, result: BaseCheckResult) -> BaseCheckResult:
        ...

    def check(self) -> BaseCheckResult:
        try:
            for _ in range(self.max_retries):
                response = self.check_server()

                if response.status == Status.normal:
                    if not response.signature:
                        response.signature = self.sign
                    return self._check_result(response)
                time.sleep(self.backoff)
            
            if not response.signature: # type: ignore
                response.signature = self.sign # type: ignore
            return self._check_result(response) # type: ignore
        except Exception as e:
            raise NotImplementedError(e)
    
    async def acheck(self) -> BaseCheckResult:
        try:
            for _ in range(self.max_retries):
                response = await self.acheck_server()

                if response.status == Status.normal:
                    if not response.signature:
                        response.signature = self.sign
                    return self._check_result(response)
                await asyncio.sleep(self.backoff)
            
            if not response.signature: # type: ignore
                response.signature = self.sign # type: ignore
            return self._check_result(response) # type: ignore
        except Exception as e:
            raise NotImplementedError(e)
    
    @abstractmethod
    def check_server(self) -> BaseCheckResult:
        ...
    
    @abstractmethod
    async def acheck_server(self) -> BaseCheckResult:
        ...
    
    @abstractmethod
    async def cleanup(self) -> None:
        ...
    
    @abstractmethod
    def make_template(self) -> str:
        ...


class Notifier(Protocol):
    def send(self, msg: Message):
        ...
    
    async def asend(self, msg: Message):
        ...
