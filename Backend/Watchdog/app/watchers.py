import random
import httpx
import time
from typing import cast

try:
    from .base import BaseWatcher
    from .models import WebCheckResult, Status, WebConfig, BaseCheckResult
except ImportError:
    from base import BaseWatcher
    from models import WebCheckResult, Status, WebConfig, BaseCheckResult


class WebWatcher(BaseWatcher):
    def __init__(self, config: WebConfig) -> None:
        super().__init__(config, 5)
        self.config: WebConfig
        self.client = httpx.Client()

    def check_server(self) -> WebCheckResult:
        try:
            status: Status

            start = time.perf_counter()
            response = self.client.get(self.config.endpoint, timeout=1)
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
            print(f"{self.config.name} server check")

            return result
        except httpx.ReadTimeout as e:
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
    
    def make_template(self) -> str:
        return """endpoint: {endpoint}\nstatus: {status}\nmessage: {message}\nlatency: {latency}"""


if __name__ == "__main__":
    web = WebWatcher(config=WebConfig(endpoint="http://localhost:8000/health"))
    sig = web._signature()
    print(sig)
    web.check_server()