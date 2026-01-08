import httpx
import time
import logging
from typing import cast

from app.core.base import BaseWatcher
from app.core.models import WebCheckResult, Status, WebConfig, BaseCheckResult

logger = logging.getLogger("WebWatcher")


class WebWatcher(BaseWatcher):
    def __init__(self, config: WebConfig) -> None:
        super().__init__(config, 5)
        self.config: WebConfig

    def check_server(self) -> WebCheckResult:
        try:
            status: Status

            start = time.perf_counter()
            with httpx.Client(timeout=30) as client:
                response = client.get(self.config.endpoint)
                
            end = time.perf_counter()

            status = Status.normal if response.status_code >= 200 and response.status_code < 300 else Status.down

            process_time = end-start
            if status is Status.normal and process_time >= float(self.config.latency):
                status = Status.latency

            result = WebCheckResult(
                status=status,
                status_code=response.status_code,
                headers=dict(**response.headers),
                body=response.json(),
                latency=process_time
            )
            logger.debug(f"{self.config.name} server check. status: {status} result: {result.body}")

            return result
        except httpx.ReadTimeout as e:
            logger.error(f"{self.config.name} server check. Timeout error for 30 sec.")
            return WebCheckResult(
                status=Status.latency,
                endpoint=self.config.endpoint,
                latency=30.0,
                error_message=str(e)
            )
    
    async def acheck_server(self) -> BaseCheckResult:
        try:
            status: Status

            start = time.perf_counter()
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(self.config.endpoint)
            end = time.perf_counter()

            status = Status.normal if response.status_code >= 200 and response.status_code < 300 else Status.down

            process_time = end-start
            if status is Status.normal and process_time >= float(self.config.latency):
                status = Status.latency

            result = WebCheckResult(
                status=status,
                status_code=response.status_code,
                headers=dict(**response.headers),
                body=response.json(),
                latency=process_time
            )
            logger.debug(f"{self.config.name} server check. status: {status} result: {result.body}")

            return result
        except httpx.ReadTimeout as e:
            logger.error(f"{self.config.name} server check. Timeout error for 30 sec.")
            return WebCheckResult(
                status=Status.latency,
                endpoint=self.config.endpoint,
                latency=30.0,
                error_message=str(e)
            )

    def _check_result(self, result: BaseCheckResult) -> BaseCheckResult:
        result = cast(WebCheckResult, result)
        if not result.endpoint:
            result.endpoint = self.config.endpoint

        return result

    async def cleanup(self) -> None:
        ...
    
    def make_template(self) -> str:
        return """endpoint: {endpoint}\nstatus: {status}\nmessage: {message}\nlatency: {latency}"""


if __name__ == "__main__":
    web = WebWatcher(config=WebConfig(endpoint="http://localhost:8000/slow"))
    # sig = web._signature()
    # print(sig)
    # result = web.check_server()
    # print(result)

    import asyncio
    async def main():
        result = await web.acheck()
        print(result)
    
    asyncio.run(main())