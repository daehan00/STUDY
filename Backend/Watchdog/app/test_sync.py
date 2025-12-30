import random

try:
    # from .base import BaseWatcher
    # from .models import WebCheckResult, Status, BaseConfig, WebConfig
    from .watchers import WebWatcher, WebConfig
    from .alert import set_notifiers, set_alert
except ImportError:
    # from base import BaseWatcher
    # from models import WebCheckResult, Status, BaseConfig, WebConfig
    from watchers import WebWatcher, WebConfig
    from alert import set_notifiers, set_alert


# class TestWatcher(BaseWatcher):
#     def __init__(self, name: str, config: BaseConfig) -> None:
#         super().__init__(config, random.randint(1, 5))
#         self.name = name

#     def check_server(self) -> WebCheckResult:
#         status = Status(random.randint(0, 2))

#         result = WebCheckResult(
#             status=status
#         )
#         return result
    
#     def make_template(self) -> str:
#         return """endpoint: {endpoint}\nstatus: {status}\nmessage: {message}\nlatency: {latency}"""


if __name__ == "__main__":
    watchers = [WebWatcher(
        config=WebConfig(
            name=f"testwatcher({i+1})",
            endpoint="http://localhost:8000/timeout",
            latency=2
        )
    ) for i in range(5)]
    watcher_dict = {watcher.sign: watcher for watcher in watchers}
    print(len(watcher_dict.items()))

    notifiers = set_notifiers()
    
    for i in range(3):
        print(f"({i+1})th iteration...")

        # watcher 목록 업데이트 로직
        for k, watcher in watcher_dict.items():
            result = watcher.check()

            msg, noti_list = set_alert(watcher, result, notifiers)

            if not msg:
                continue
            
            print(watcher.config.name)
            for noti in noti_list:
                print(noti.__class__.__name__)
                noti.send(msg)
            