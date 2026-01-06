import asyncio
import json
import datetime
from pathlib import Path
from collections import deque
from typing import Deque
from pydantic import BaseModel, Field

try:
    from app.core.models import MessageGrade, Status
    from app.config.settings import MAX_LOG, LOCAL_TZ, DATA_VERSION, LOG_DATA_FILE
except ImportError:
    from models import MessageGrade, Status
    DATA_VERSION = "1.0"
    LOG_DATA_FILE = Path(__file__).parent / "log.json"
    MAX_LOG = 100
    LOCAL_TZ = datetime.datetime.now().astimezone().tzinfo


class LogEntry(BaseModel):
    """로그 데이터 구조"""
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(LOCAL_TZ).isoformat(timespec='seconds'))
    source: str  # Watcher 이름 또는 ID
    event: MessageGrade   # check_start, check_end, status_change 등
    details: dict | str # 상세 정보
    level: str = "INFO"

    def to_string(self) -> str:
        """로그를 문자열로 변환 (포맷팅)"""
        detail_str = json.dumps(self.details, ensure_ascii=False) if isinstance(self.details, dict) else str(self.details)
        return f"[{self.timestamp}] [{self.level}] [{self.source}] {self.event}: {detail_str}"


class LogManager:
    """Singleton pattern의 로그 관리 클래스"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        
        self.log: Deque[LogEntry] = deque(maxlen=MAX_LOG)
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(5)
        self._initialized = True
        self._running = False
        self.save_interval = 10
        self._file_manager = FileManager(LOG_DATA_FILE)
        self._load_saved_logs()
    
    async def start(self) -> None:
        self._running = True
        asyncio.create_task(self._periodic_save())
    
    async def stop(self) -> None:
        self._running = False
        
    async def aadd_log(self, **kwargs) -> str:
        data = LogEntry(**kwargs)
        async with self._lock:
            self.log.append(data)
        return data.to_string()
    
    def add_log(self, **kwargs) -> str:
        data = LogEntry(**kwargs)
        self.log.append(data)
        return data.to_string()
    
    def get_logs(self, source: str, max_count: int = 10) -> list[str]:
        filtered = [
            log.to_string()
            for log in reversed(self.log) if log.source == source
        ]
        return filtered[:max_count]
    
    async def _periodic_save(self) -> None:
        while self._running:
            await asyncio.sleep(self.save_interval)
            await self._save_to_json()
    
    async def _save_to_json(self) -> None:
        loop = asyncio.get_running_loop()

        async with self._lock:
            data_to_save = [l.model_dump() for l in self.log]
        
        # 별도 스레드에서 파일 쓰기 수행 (Non-blocking)
        await loop.run_in_executor(None, self._file_manager.save, data_to_save)
    
    def _load_saved_logs(self) -> None:
        log_list = self._file_manager.load()
        for item in log_list:
            self.log.append(LogEntry(**item))
    
    def get_all_logs(self) -> list[str]:
        result = []
        for i in self.log:
            print(i.to_string())
            result.append(i.to_string())
        
        return result


class Logger:
    def __init__(self, signature: str) -> None:
        self.sign = signature
        self.log_manager = log_manager
    
    def info(self, event, details):
        self.log_manager.add_log(
            source=self.sign,
            event=event,
            details=details,
            level="INFO"
        )

    async def ainfo(
        self, event: MessageGrade = MessageGrade.etc,
        details: dict | str = ""
    ):
        await self.log_manager.aadd_log(
            source=self.sign,
            event=event,
            details=details,
            level="INFO"
        )

    def warning(
        self, event: MessageGrade = MessageGrade.etc,
        details: dict | str = ""
    ):
        self.log_manager.add_log(
            source=self.sign,
            event=event,
            details=details,
            level="WARNING"
        )

    async def awarning(
        self, event: MessageGrade = MessageGrade.etc,
        details: dict | str = ""
    ):
        await self.log_manager.aadd_log(
            source=self.sign,
            event=event,
            details=details,
            level="WARNING"
        )

    def error(
        self, event: MessageGrade = MessageGrade.etc,
        details: dict | str = ""
    ):
        self.log_manager.add_log(
            source=self.sign,
            event=event,
            details=details,
            level="ERROR"
        )

    async def aerror(
        self, event: MessageGrade = MessageGrade.etc,
        details: dict | str = ""
    ):
        await self.log_manager.aadd_log(
            source=self.sign,
            event=event,
            details=details,
            level="ERROR"
        )


class FileManager:
    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.data_version = DATA_VERSION
        self._ensure_data_file()
    
    def _ensure_data_file(self) -> None:
        """데이터 파일이 존재하는지 확인하고 없으면 생성"""
        if not self.data_file.exists():
            # 디렉토리가 없으면 생성
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 초기 데이터 구조 생성
            initial_data = {
                "version": self.data_version,
                "data": []
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)

    def load(self) -> list:
        """JSON 파일에서 서버 데이터 로드"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("data", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"데이터 로드 오류: {e}")
            return []
    
    def save(self, data: list) -> None:
        """현재 서버 데이터를 JSON 파일에 저장"""
        in_data = {
            "version": self.data_version,
            "data": data,
        }
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(in_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"데이터 저장 오류: {e}")
            raise

log_manager = LogManager()

if __name__ == "__main__":
    logger = LogManager()

    async def main():
        logs = [LogEntry(
            source=f"testinstance({i})",
            event=MessageGrade.critical,
            details={"status": Status.down.name},
            level="INFO"
        ) for i in range(10000)]

        tasks = [logger.aadd_log(*log) for log in logs]

        await asyncio.gather(*tasks)

        await logger._save_to_json()
    
    import time
    s = time.perf_counter_ns()
    # asyncio.run(main())
    logs = logger.get_logs("testinstance(9999)")
    print(logs)
    e = time.perf_counter_ns()
    print(e-s)

# 59886416
# 59751250
# 58695083