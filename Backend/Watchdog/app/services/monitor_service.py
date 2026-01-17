import asyncio
import time
import logging
from typing import Any, Dict, Set, Optional, Tuple

from app.services.server_service import ServerService
from app.core.base import BaseWatcher
from app.core.web_watcher import WebWatcher
from app.core.db_watcher import DBWatcher
from app.core.models import WebConfig, DBConfig, Status, MessageGrade, BaseCheckResult
from app.utils.server_logger import CustomLogger, LogManager

logger = logging.getLogger("MonitorService")
log_manager = LogManager()

class MonitorService:
    """서버 모니터링 서비스 (Singleton)"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.is_running = False
        self.watchers: Dict[str, BaseWatcher] = {}
        self.logger = CustomLogger("MonitorService")
        self.logger.info(MessageGrade.start, "Initialized!")
            
        self.server_service = ServerService()
        self.check_interval = 30  # 30초마다 체크
        self.main_task: Optional[asyncio.Task] = None
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(5)
        self._last_server_ids: Set[str] = set()
        
        # 메모리 캐시 및 I/O 최적화
        self.status_cache: Dict[str, str] = {}  # server_id -> status
        self.dirty_servers: Set[str] = set()  # 변경된 서버 ID
        self.last_save_time = time.time()
        self.save_interval = 300  # 5분
        self.save_threshold = 10  # 10건 변경 시 저장
        
        # 동기화용 Lock
        self.watchers_lock = asyncio.Lock()
        
        # 이벤트 리스너
        self.listeners = []
        
        # ServerService 변경 감지 리스너 등록
        self.server_service.add_listener(self._on_server_data_changed)
        
        self._initialized = True

        logger.debug("initialized!!")
    
    def _on_server_data_changed(self, event_type: str, server_data: Dict):
        """서버 데이터 변경 시 호출되는 콜백"""
        if not self.is_running:
            return

        server_id = server_data['id']
        server_name = server_data.get('name', 'Unknown')
        is_enabled = server_data.get('is_monitoring_enabled', True)

        logger.info(f"Server data changed: {event_type} - {server_name} (Enabled: {is_enabled})")

        if event_type == "delete":
            if server_id in self.watchers:
                self.watchers[server_id].logger.info(
                    MessageGrade.etc,
                    f"Removed watcher for deleted server: {server_name}"
                )
                
                del self.watchers[server_id]
                if server_id in self.status_cache:
                    del self.status_cache[server_id]
                logger.info(f"Removed watcher for deleted server: {server_name}")

        elif event_type == "add":
            if is_enabled and server_id not in self.watchers:
                watcher = self._create_watcher(server_data)
                if watcher:
                    self.watchers[server_id] = watcher
                    self.status_cache[server_id] = server_data.get('status', 'active')
                    watcher.logger.info(
                        MessageGrade.etc,
                        f"Added watcher for new server: {server_name}"
                    )
                    logger.info(f"Added watcher for new server: {server_name}")

        elif event_type == "update":
            # 모니터링 비활성화된 경우 제거
            if not is_enabled:
                if server_id in self.watchers:
                    self.watchers[server_id].logger.info(
                        MessageGrade.etc,
                        f"Removed watcher (disabled): {server_name}"
                    )
                    del self.watchers[server_id]
                    logger.info(f"Removed watcher (disabled): {server_name}")
            else:
                # 활성화 상태인 경우 Watcher 재생성 및 교체
                # (설정이 변경되었을 수 있으므로 무조건 재생성)
                watcher = self._create_watcher(server_data)
                if watcher:
                    self.watchers[server_id] = watcher
                    # 상태 캐시는 유지하거나 초기화 (여기서는 유지)
                    # watcher.logger.info(
                    #     MessageGrade.etc,
                    #     f"Updated watcher for server: {server_name}"
                    # )
                    # logger.info(f"Updated watcher for server: {server_name}")

    def add_listener(self, callback):
        """상태 변경 리스너 추가"""
        if callback not in self.listeners:
            self.listeners.append(callback)
            
    def remove_listener(self, callback):
        """상태 변경 리스너 제거"""
        if callback in self.listeners:
            self.listeners.remove(callback)
            
    def _notify_listeners(self, server_id: str, status: str):
        """리스너들에게 상태 변경 알림"""
        for listener in self.listeners:
            try:
                listener(server_id, status)
            except Exception as e:
                logger.error(f"Error in listener: {e}")

    async def start(self):
        """모니터링 시작"""
        if self.is_running:
            logger.info("Monitoring is already running")
            return
        
        try:
            await log_manager.start()
            self.is_running = True
            self._load_servers()
            
            # 서버가 0개인 경우 예외 발생
            if len(self.watchers) == 0:
                self.is_running = False
                await log_manager.stop()
                raise ValueError("모니터링할 서버가 없습니다. 먼저 서버를 추가해주세요.")
            
            self.logger.info(
                MessageGrade.start,
                f"Monitoring started with {len(self.watchers)} servers"
            )
            logger.info(f"Monitoring started with {len(self.watchers)} servers")
            
            # 메인 모니터링 루프 시작
            self.main_task = asyncio.create_task(self._monitor_loop())
            
        except ValueError:
            # ValueError는 그대로 전달 (UI에서 처리)
            raise
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """모니터링 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.main_task:
            self.main_task.cancel()
            try:
                await self.main_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error while cancelling monitor task: {e}")
        
        # Watcher 리소스 정리 (DB 연결 종료 등)
        for watcher in self.watchers.values():
            if hasattr(watcher, 'cleanup'):
                try:
                    await watcher.cleanup()
                except Exception as e:
                    logger.error(f"Failed to cleanup watcher: {e}")

        self.watchers.clear()
        self.status_cache.clear()
        self.dirty_servers.clear()
        
        self.logger.info(
            MessageGrade.stop,
            "Monitoring stopped"
        )
        await log_manager.stop()
        logger.info("Monitoring stopped")
    
    def _load_servers(self):
        """서버 목록 로드 및 Watcher 생성"""
        try:
            servers = self.server_service.get_all_servers()
            
            # is_monitoring_enabled가 True인 서버만 필터링
            enabled_servers = [
                s for s in servers 
                if s.get('is_monitoring_enabled', True)
            ]
            
            success_count = 0
            fail_count = 0
            
            for server in enabled_servers:
                server_id = server['id']
                server_name = server.get('name', 'Unknown')
                
                if server_id not in self.watchers:
                    try:
                        watcher = self._create_watcher(server)
                        if watcher:
                            self.watchers[server_id] = watcher
                            # 초기 상태 캐시
                            self.status_cache[server_id] = server.get('status', 'active')
                            success_count += 1
                            watcher.logger.info(
                                MessageGrade.etc,
                                f"Added watcher for server: {server_name}"
                            )
                        else:
                            logger.warning(f"Failed to create watcher for server '{server_name}' (ID: {server_id})")
                            fail_count += 1
                    except Exception as e:
                        logger.error(f"Exception while creating watcher for '{server_name}': {e}")
                        fail_count += 1
            
            self._last_server_ids = set(s['id'] for s in enabled_servers)
            
            if success_count > 0:
                logger.info(f"Loaded {success_count} watchers successfully")
            if fail_count > 0:
                logger.warning(f"Failed to load {fail_count} watchers")
                
        except Exception as e:
            logger.error(f"Failed to load servers: {e}")
            raise
    
    def _create_watcher(self, server_data: Dict) -> Optional[BaseWatcher]:
        """서버 데이터로부터 Watcher 인스턴스 생성"""
        server_type = server_data.get('server_type')
        server_name = server_data.get('name', 'Unknown')
        
        try:
            if server_type == 'web':
                config = WebConfig(
                    name=server_name,
                    endpoint=f"{server_data.get('url', '')}{f":{server_data.get('port')}" if server_data.get('port') else ""}{server_data.get('endpoint', '')}",
                    latency=int(server_data.get('latency', 30)),
                    auth_key=server_data.get('auth_key')
                )
                return WebWatcher(config)
            
            elif server_type == 'db':
                config = DBConfig(
                    name=server_name,
                    host=server_data.get('host', server_data.get('host', 'localhost')),
                    port=int(server_data.get('poert', server_data.get('port', 5432))),
                    username=server_data.get('username', server_data.get('username', '')),
                    password=server_data.get('password', server_data.get('password', '')),
                    dbms=server_data.get('dbms', server_data.get('dbms', 'postgresql')),
                    db_name=server_data.get('db_name', server_data.get('db_name', ''))
                )
                return DBWatcher(config)
            
            else:
                logger.warning(f"Unknown server type '{server_type}' for server '{server_name}'")
                return None
            
        except KeyError as e:
            logger.error(f"Missing required field {e} for server '{server_name}'")
            return None
        except ValueError as e:
            logger.error(f"Invalid value for server '{server_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create watcher for '{server_name}': {type(e).__name__}: {e}")
            return None
    
    async def _monitor_loop(self):
        """메인 모니터링 루프"""
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        try:
            while self.is_running:
                try:
                    # 서버 목록 동기화
                    await self._sync_servers()
                    
                    # Watchers의 스냅샷 획득 (동기화 이슈 방지)
                    async with self.watchers_lock:
                        current_watchers = dict(self.watchers)
                    
                    # 서버가 0개인 경우 대기만 수행
                    if not current_watchers:
                        # print("[DEBUG] No servers to monitor, waiting...")  # 과도한 로그 방지
                        await asyncio.sleep(self.check_interval)
                        continue
                    
                    # 스냅샷으로 체크 수행 (Lock 없이)
                    tasks = [
                        self._check_server(server_id, watcher)
                        for server_id, watcher in current_watchers.items()
                    ]
                    
                    # 모든 체크 결과 수집 (예외도 포함)
                    async with self.semaphore:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # 실패한 체크 확인
                    failed_checks = sum(1 for r in results if isinstance(r, Exception))
                    if failed_checks > 0:
                        logger.warning(f"{failed_checks}/{len(tasks)} server checks failed")
                    
                    # 조건부 저장
                    await self._conditional_save()
                    
                    # 에러 카운터 리셋 (정상 실행 완료)
                    consecutive_errors = 0
                    
                    # 다음 체크까지 대기
                    await asyncio.sleep(self.check_interval)
                    
                except asyncio.CancelledError:
                    logger.info("Monitor loop cancelled")
                    break
                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Monitor loop error ({consecutive_errors}/{max_consecutive_errors}): {type(e).__name__}: {e}")
                    
                    # 연속 에러가 너무 많으면 모니터링 중지
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Too many consecutive errors. Stopping monitoring.")
                        self.is_running = False
                        break
                    
                    # 백오프 전략: 에러 횟수에 비례하여 대기 시간 증가
                    backoff_time = min(self.check_interval * consecutive_errors, 300)  # 최대 5분
                    await asyncio.sleep(backoff_time)
        finally:
            # 루프 종료 시 (에러, 취소 등) 상태 저장
            logger.info("Monitor loop finished. Saving final states...")
            try:
                await self._save_states()
                await self.logger.log_manager._save_to_json()
            except Exception as e:
                logger.error(f"Failed to save states on loop exit: {e}")
    
    async def _sync_servers(self):
        """서버 목록 동기화 (안전하게)"""
        try:
            current_servers = self.server_service.get_all_servers()
            
            # is_monitoring_enabled가 True인 서버만 필터링
            enabled_servers = [
                s for s in current_servers 
                if s.get('is_monitoring_enabled', True)
            ]
            
            current_ids = set(s['id'] for s in enabled_servers)
            
            async with self.watchers_lock:
                # 현재 Watchers의 복사본 생성
                new_watchers = dict(self.watchers)
                
                # 삭제된 서버 또는 비활성화된 서버 제거
                removed_ids = set(new_watchers.keys()) - current_ids
                for server_id in removed_ids:
                    del new_watchers[server_id]
                    # 캐시에서도 제거
                    self.status_cache.pop(server_id, None)
                    self.dirty_servers.discard(server_id)
                    logger.info(f"Server {server_id} removed from monitoring")
                
                # 새로 추가된 서버 또는 활성화된 서버 등록
                for server in enabled_servers:
                    server_id = server['id']
                    server_name = server.get('name', 'Unknown')
                    
                    if server_id not in new_watchers:
                        try:
                            watcher = self._create_watcher(server)
                            if watcher:
                                new_watchers[server_id] = watcher
                                self.status_cache[server_id] = server.get('status', 'active')
                                watcher.logger.info(
                                    MessageGrade.etc,
                                    f"Added watcher for server: {server_name}"
                                )
                                logger.warning(f"Server '{server_name}' (ID: {server_id}) added to monitoring")
                            else:
                                logger.warning(f"Failed to add server '{server_name}' to monitoring")
                        except Exception as e:
                            logger.error(f"Failed to add server '{server_name}': {e}")
                
                # 원자적으로 교체
                self.watchers = new_watchers
                self._last_server_ids = current_ids
                
        except Exception as e:
            logger.error(f"Failed to sync servers: {e}")
            # 동기화 실패해도 기존 watchers는 유지
    
    async def _check_server(self, server_id: str, watcher: BaseWatcher) -> Tuple[str, Optional[Any]]:
        """개별 서버 헬스체크"""
        try:
            result = await watcher.acheck()
            
            # 상태 매핑
            status_map = {
                Status.normal: "active",
                Status.latency: "warning",
                Status.down: "inactive"
            }
            
            new_status = status_map.get(result.status, "active")
            old_status = self.status_cache.get(server_id)
            
            # 상태가 변경된 경우만 처리
            if old_status != new_status:
                self._update_change(server_id, old_status, new_status, watcher, result)
            
            return (server_id, result)
            
        except asyncio.TimeoutError:
            msg = f"Timeout checking server {server_id} ({watcher.config.name})"
            logger.error(msg)
            # 타임아웃 시 inactive로 처리
            old_status = self.status_cache.get(server_id)
            new_status = "inactive"
            
            if old_status != new_status:
                self._update_change(server_id, old_status, new_status, watcher, error_message=msg)
                
            return (server_id, None)
        except ConnectionError as e:
            msg = f"Connection error for server {server_id} ({watcher.config.name}): {e}"
            logger.error(msg)
            old_status = self.status_cache.get(server_id)
            new_status = "inactive"
            
            if old_status != new_status:
                self._update_change(server_id, old_status, new_status, watcher, error_message=msg)
                
            return (server_id, None)
        except Exception as e:
            msg = f"Unexpected error checking server {server_id} ({watcher.config.name}): {type(e).__name__}: {e}"
            logger.error(msg)
            
            # 예기치 않은 에러도 서버 다운으로 간주
            old_status = self.status_cache.get(server_id)
            new_status = "inactive"
            
            if old_status != new_status:
                self._update_change(server_id, old_status, new_status, watcher, error_message=msg)
                
            return (server_id, None)
    
    def _update_change(
        self, server_id: str, old_status: str | None,
        new_status: str, watcher: BaseWatcher,
        result: BaseCheckResult | None = None,
        error_message: str | None = None
    ) -> None:
        self.status_cache[server_id] = new_status
        self.dirty_servers.add(server_id)

        detail = result.model_dump() if result else error_message
        if isinstance(detail, dict):
            detail["status"] = detail["status"].name

        event = MessageGrade.resolved

        if new_status == "inactive":
            event = MessageGrade.critical
        
        if new_status == "warning":
            event = MessageGrade.warning

        watcher.logger.info(event, detail)
        logger.info(f"Server {server_id} ({watcher.config.name}) status changed: {old_status} -> {new_status}")
        self._notify_listeners(server_id, new_status)

    async def _conditional_save(self):
        """조건부 파일 저장"""
        current_time = time.time()
        time_elapsed = current_time - self.last_save_time
        
        # 조건: 시간 경과 또는 변경 건수 초과
        if (time_elapsed >= self.save_interval or 
            len(self.dirty_servers) >= self.save_threshold):
            await self._save_states()
    
    async def _save_states(self):
        """변경된 상태를 파일에 저장"""
        if not self.dirty_servers:
            return
        
        # 백그라운드에서 I/O 수행
        dirty_copy = set(self.dirty_servers)
        success_count = 0
        fail_count = 0
        
        for server_id in dirty_copy:
            status = self.status_cache.get(server_id)
            if status:
                try:
                    self.server_service.update_server(server_id, {"status": status})
                    success_count += 1
                except FileNotFoundError as e:
                    logger.error(f"Server data file not found while saving {server_id}: {e}")
                    fail_count += 1
                except PermissionError as e:
                    logger.error(f"Permission denied while saving {server_id}: {e}")
                    fail_count += 1
                except Exception as e:
                    logger.error(f"Failed to save status for {server_id}: {type(e).__name__}: {e}")
                    fail_count += 1
        
        self.dirty_servers.clear()
        self.last_save_time = time.time()
        
        if success_count > 0:
            logger.info(f"States saved to file ({success_count} servers)")
        if fail_count > 0:
            logger.warning(f"Failed to save {fail_count} server states")
    
    def get_status(self) -> Dict:
        """현재 모니터링 상태 반환"""
        return {
            "is_running": self.is_running,
            "monitored_servers": len(self.watchers),
            "dirty_servers": len(self.dirty_servers),
            "last_save": self.last_save_time,
        }
