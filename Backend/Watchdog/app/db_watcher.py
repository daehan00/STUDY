import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

try:
    from .base import BaseWatcher
    from .models import DBCheckResult, Status, DBConfig, BaseCheckResult
except ImportError:
    from base import BaseWatcher
    from models import DBCheckResult, Status, DBConfig, BaseCheckResult


class DBWatcher(BaseWatcher):
    def __init__(self, config: DBConfig) -> None:
        super().__init__(config, 1)
        self.config: DBConfig
        self.engine = create_engine(self._process_dbms(config), pool_timeout=3)
        self.result_template = DBCheckResult(
            status=Status.normal,
            dbms=self.config.dbms,
            db_name=self.config.db_name,
            username=self.config.username,
        )

    def _process_dbms(self, config: DBConfig) -> str:
        url = ""
        password = urllib.parse.quote_plus(config.password)
        if config.dbms == "mysql":
            url = f"{config.dbms}+pymysql://{config.username}:{password}@{config.host}:{config.port}/{config.db_name}"
        
        if config.dbms == "postgresql":
            url = f"{config.dbms}+psycopg://{config.username}:{password}@{config.host}:{config.port}/{config.db_name}"

        if not url:
            raise KeyError(f"UnSupported or Wrong dbms: [{config.dbms}]")

        return url

    def check_server(self) -> DBCheckResult:
        check_result = self.result_template.model_copy()
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))

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

    watcher.check_server()


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

    watcher1.check_server()