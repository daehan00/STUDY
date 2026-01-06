import enum
from pydantic import BaseModel, Field


class BaseConfig(BaseModel):
    name: str | None = Field(default=None)
    ...


class WebConfig(BaseConfig):
    endpoint: str
    latency: int = Field(default=30)
    auth_key: str | None = Field(default=None)


class DBConfig(BaseConfig):
    host: str
    port: int = Field(default=3306)
    username: str
    password: str
    dbms: str
    db_name: str


class Status(enum.IntEnum):
    normal=0
    latency=1
    down=2


class BaseCheckResult(BaseModel):
    signature: tuple | None = Field(default=None)
    status: Status
    message: str | None = Field(default=None)
    error_message: str | None = Field(default=None)


class WebCheckResult(BaseCheckResult):
    endpoint: str | None = Field(default=None)
    latency: float | None = Field(default=None)
    status_code: int | None = Field(default=None)
    headers: dict | None = Field(default=None)
    body: dict | None = Field(default=None)


class DBCheckResult(BaseCheckResult):
    dbms: str
    db_name: str
    username: str
    error_code: str | None = Field(default=None)


class WorkerCheckResult(BaseCheckResult):
    name: str


class MessageGrade(enum.StrEnum):
    resolved="resolved"
    warning="warning"
    critical="critical"
    start="start"
    stop="stop"
    etc="etc"


class Message(BaseModel):
    grade: MessageGrade
    title: str | None = Field(default=None)
    body: str
    config: dict | None = Field(default={})


if __name__ == "__main__":
    statuses = [Status.normal, Status.down, Status.latency]
    statuses.sort(key=lambda x: x.value)
    print(statuses)