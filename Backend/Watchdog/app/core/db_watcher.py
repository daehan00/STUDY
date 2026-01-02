import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.core.base import BaseWatcher
from app.core.models import DBCheckResult, Status, DBConfig, BaseCheckResult


class DBWatcher(BaseWatcher):
    def __init__(self, config: DBConfig) -> None:
        super().__init__(config, 1)
        self.config: DBConfig
        self.engine = create_engine(self._make_url(config), pool_timeout=3)
        self.aengine = create_async_engine(self._make_url(config, False), pool_timeout=3)
        self.result_template = DBCheckResult(
            status=Status.normal,
            dbms=self.config.dbms,
            db_name=self.config.db_name,
            username=self.config.username,
        )

    def _make_url(self, config: DBConfig, sync: bool = True) -> str:
        url = ""
        password = urllib.parse.quote_plus(config.password)
        if config.dbms == "mysql":
            url = f"{config.dbms}+pymysql://{config.username}:{password}@{config.host}:{config.port}/{config.db_name}"

            if not sync:
                url = url.replace("pymysql", "aiomysql")
        
        if config.dbms == "postgresql":
            url = f"{config.dbms}+psycopg://{config.username}:{password}@{config.host}:{config.port}/{config.db_name}"

        if not url:
            raise KeyError(f"UnSupported or Wrong dbms: [{config.dbms}]")

        return url

    def check_server(self) -> DBCheckResult:
        check_result = self.result_template.model_copy()
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

        except OperationalError as e:
            print(f"운영 에러 발생! 원인:\n{e.orig}") # DB 드라이버의 실제 메시지
            print(f"에러 코드: {e.code}")           # SQLAlchemy 고유 에러 코드
            check_result.error_code = str(e.orig)
            check_result.error_message = str(e.orig)
            check_result.status = Status.down
        except SQLAlchemyError as e:
            check_result.error_message = e.args[0].split('"')[1]
            check_result.status = Status.down
            print(f"기타 DB 에러: {check_result.error_message}")
        
        print(f"{self.config.name} check")
        return check_result

    async def acheck_server(self) -> DBCheckResult:
        check_result = self.result_template.model_copy()
        try:
            async with self.aengine.connect() as conn:
                await conn.execute(text("SELECT 1"))

        except OperationalError as e:
            print(f"운영 에러 발생! 원인:\n{e.orig}") # DB 드라이버의 실제 메시지
            print(f"에러 코드: {e.code}")           # SQLAlchemy 고유 에러 코드
            check_result.error_code = str(e.orig)
            check_result.error_message = str(e.orig)
            check_result.status = Status.down
        except SQLAlchemyError as e:
            check_result.error_message = e.args[0].split('"')[1]
            check_result.status = Status.down
            print(f"기타 DB 에러: {check_result.error_message}")
        
        print(f"{self.config.name} check")
        return check_result

    async def cleanup(self) -> None:
        self.engine.dispose()
        await self.aengine.dispose()

    def _check_result(self, result: BaseCheckResult) -> BaseCheckResult:
        return result

    def make_template(self) -> str:
        return """DB info:\n DBMS: {dbms}\n DB name: {db_name}\n\nError Code: {error_code}\nError Message: {error_message}"""


if __name__ == "__main__":
    # # 1. 엔진 생성 (재활용을 위한 커넥션 풀이 자동 생성됨)
    # engine = create_engine("mysql+pymysql://readonly_user:readonly_password@localhost:3306/testdb")

    # # 2. 안전한 실행 (Context Manager 사용)
    # try:
    #     with engine.connect() as conn:
    #         result = conn.execute(text("SELECT 1"))
    #         print(result.fetchone())
    #         print(result.fetchmany(3))
    #         print(result.keys())
    # except OperationalError as e:
    #     print(f"운영 에러 발생! 원인: {e.orig}") # DB 드라이버의 실제 메시지
    #     print(f"에러 코드: {e.code}")           # SQLAlchemy 고유 에러 코드
    # except SQLAlchemyError as e:
    #     print(f"기타 DB 에러: {e.args[0].split('"')[1]}")
    # # with 블록이 끝나면 연결은 자동으로 '풀'로 반환되어 재활용됩니다.

    watcher = DBWatcher(
        config=DBConfig(
            name="database1",
            dbms="mysql",
            username="readonly_user",
            password="readonly_password",
            host="localhost",
            db_name="testdb"
        )
    )
    # watcher.check_server()

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
    # watcher1.check_server()

    import asyncio
    async def main():
        tasks = [w.acheck() for w in [watcher, watcher1]]

        await asyncio.gather(*tasks)
        print("작업 완료")
        
        await asyncio.gather(
            watcher.cleanup(),
            watcher1.cleanup()
        )
    
    asyncio.run(main())
