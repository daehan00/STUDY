import enum
from pydantic import BaseModel, Field


class BaseConfig(BaseModel):
    name: str | None = Field(default=None)
    ...


class WebConfig(BaseConfig):
    endpoint: str
    auth_key: str | None = Field(default=None)


class Status(enum.IntEnum):
    normal=0
    latency=1
    down=2


class BaseCheckResult(BaseModel):
    signature: str | None = Field(default=None)
    status: Status
    message: str | None = Field(default=None)


class WebCheckResult(BaseCheckResult):
    endpoint: str | None = Field(default=None)
    latency: float | None = Field(default=None)


class DBCheckResult(BaseCheckResult):
    dbms: str
    user: str
    error_code: int


class WorkerCheckResult(BaseCheckResult):
    name: str


if __name__ == "__main__":
    statuses = [Status.normal, Status.down, Status.latency]
    statuses.sort(key=lambda x: x.value)
    print(statuses)