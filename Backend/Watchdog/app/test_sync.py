import random

try:
    from .base import BaseWatcher
    # from .models import WebCheckResult, Status, BaseConfig, WebConfig
    from .web_watcher import WebWatcher, WebConfig
    from .db_watcher import DBWatcher, DBConfig
    from .alert import set_notifiers, set_alert
except ImportError:
    from base import BaseWatcher
    # from models import WebCheckResult, Status, BaseConfig, WebConfig
    from web_watcher import WebWatcher, WebConfig
    from db_watcher import DBWatcher, DBConfig
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
    watchers: list[BaseWatcher] = [WebWatcher(
        config=WebConfig(
            name=f"testwatcher({i+1})",
            endpoint="http://localhost:8000/health",
            latency=2
        )
    ) for i in range(5)]

    watcher = DBWatcher(
        config=DBConfig(
            name="database1",
            dbms="mysql",
            username="readonly_user",
            password="readonly_password",
            host="localhost",
            port=3306,
            db_name="testdb"
        )
    )
    watcher1 = DBWatcher(
        config=DBConfig(
            name="database2",
            dbms="postgresql",
            username="readonly_pg_user",
            password="readonly_pg_password",
            host="localhost",
            port=5432,
            db_name="test_pgdb"
        )
    )
    watchers.append(watcher)
    watchers.append(watcher1)

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
            