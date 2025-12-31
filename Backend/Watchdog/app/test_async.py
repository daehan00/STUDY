import asyncio

try:
    from .base import BaseWatcher, Notifier
    from .web_watcher import WebWatcher, WebConfig
    from .db_watcher import DBWatcher, DBConfig
    from .alert import set_notifiers, set_alert
except ImportError:
    from base import BaseWatcher, Notifier
    from web_watcher import WebWatcher, WebConfig
    from db_watcher import DBWatcher, DBConfig
    from alert import set_notifiers, set_alert

def set_watcher_dict() -> dict[tuple, BaseWatcher]:
    watchers: list[BaseWatcher] = [WebWatcher(
        config=WebConfig(
            name=f"testserver({i+1})",
            endpoint="http://localhost:8000/error",
            latency=2
        )
    ) for i in range(3)]

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
    return watcher_dict

async def check_and_send(watcher: BaseWatcher, notifiers: dict) -> None:
    result = await watcher.acheck()

    msg, noti_list = set_alert(watcher, result, notifiers)

    if not msg:
        return
    
    print(watcher.config.name)
    async def send_msg(noti: Notifier, msg):
        print(noti.__class__.__name__)
        await noti.asend(msg)
    
    tasks = [send_msg(noti, msg) for noti in noti_list]
    await asyncio.gather(*tasks)
    
async def main():
    watchers = set_watcher_dict()

    notifiers = set_notifiers()

    tasks = [check_and_send(watcher, notifiers) for k, watcher in watchers.items()]

    await asyncio.gather(*tasks)

    await asyncio.gather(
        *[watcher.cleanup() for k, watcher in watchers.items()]
    )

if __name__ == "__main__":
    asyncio.run(main())
