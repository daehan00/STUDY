import random

try:
    from .base import BaseWatcher, make_message_text, Notifier
    from .models import WebCheckResult, Status, BaseConfig
    from .notifier import EmailNotifier, SlackNotifier
except ImportError:
    from base import BaseWatcher, make_message_text, Notifier
    from models import WebCheckResult, Status, BaseConfig
    from notifier import EmailNotifier, SlackNotifier


class TestWatcher(BaseWatcher):
    def __init__(self, name: str, config: BaseConfig) -> None:
        super().__init__(config, random.randint(1, 5))
        self.name = name

    def check_server(self) -> WebCheckResult:
        status = Status(random.randint(0, 2))

        result = WebCheckResult(
            status=status
        )
        return result


if __name__ == "__main__":
    watchers = [TestWatcher(f"testwatcher({i+1})", config=BaseConfig(name=f"testwatcher({i+1})")) for i in range(5)]
    watcher_dict = {watcher.signature(): watcher for watcher in watchers}
    print(len(watcher_dict.items()))

    notifiers: dict[Status, list[Notifier]] = {
        Status.latency: [EmailNotifier()],
        Status.down: [EmailNotifier(), SlackNotifier()],
        Status.normal: [SlackNotifier()]
    }

    
    for i in range(10):
        print(f"({i+1})th iteration...")

        # watcher 목록 업데이트 로직

        for k, watcher in watcher_dict.items():
            result = watcher.check()
            level = result.status.value - watcher.status.value
            if level == 0:
                continue

            # 새로운 상태 업데이트
            watcher.status = result.status
            body = make_message_text(result)
            title = f"title: [{watcher.name}]"
            if level < 0:
                title += " resolved!"

            if result.status == Status.down:
                title += "down!!!!"
            
            if result.status == Status.latency:
                title += "latency!"
            
            for noti in notifiers[result.status]:
                noti.send(title+"\n"+body)

            