try:
    from .base import BaseWatcher
    from .models import WebCheckResult, Status, WebConfig
except ImportError:
    from base import BaseWatcher
    from models import WebCheckResult, Status, WebConfig


class WebWatcher(BaseWatcher):
    def __init__(self, config: WebConfig) -> None:
        super().__init__(config, 5)

    def check_server(self) -> WebCheckResult:
        result = WebCheckResult(
            status=Status.latency
        )
        print("check")

        return result
    
    def make_template(self) -> str:
        return """endpoint: {endpoint}\nstatus: {status}\nmessage: {message}\nlatency: {latency}"""


if __name__ == "__main__":
    web = WebWatcher(config=WebConfig(endpoint="https://daehan.com"))
    sig = web.signature()
    print(sig)
    web.check()