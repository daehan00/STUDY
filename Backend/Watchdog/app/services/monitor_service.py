import asyncio
import time
import sys
from pathlib import Path
from typing import Dict, Set, Optional, Tuple

# 부모 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).parent.parent))

from services.server_service import ServerService
from core.base import BaseWatcher
from core.web_watcher import WebWatcher
from core.db_watcher import DBWatcher
from core.models import WebConfig, DBConfig, Status


class MonitorService:
    """서버 모니터링 서비스 (Singleton)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.is_running = False
        self.watchers: Dict[str, BaseWatcher] = {}
        self.server_service = ServerService()
        self.check_interval = 30  # 30초마다 체크
        self.main_task: Optional[asyncio.Task] = None
        self._last_server_ids: Set[str] = set()
        
        # 메모리 캐시 및 I/O 최적화
        self.status_cache: Dict[str, str] = {}  # server_id -> status
        self.dirty_servers: Set[str] = set()  # 변경된 서버 ID
        self.last_save_time = time.time()
        self.save_interval = 300  # 5분
        self.save_threshold = 10  # 10건 변경 시 저장
        
        # 동기화용 Lock
        self.watchers_lock = asyncio.Lock()
        
        self._initialized = True
    
    async def start(self):
        """모니터링 시작"""
        if self.is_running:
            print("Monitoring is already running")
            return
        
        self.is_running = True
        self._load_servers()
        
        print(f"Monitoring started with {len(self.watchers)} servers")
        
        # 메인 모니터링 루프 시작
        self.main_task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        """모니터링 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 중지 전 모든 변경사항 저장
        await self._save_states()
        
        if self.main_task:
            self.main_task.cancel()
            try:
                await self.main_task
            except asyncio.CancelledError:
                pass
        
        self.watchers.clear()
        self.status_cache.clear()
        self.dirty_servers.clear()
        
        print("Monitoring stopped")
    
    def _load_servers(self):
        """서버 목록 로드 및 Watcher 생성"""
        servers = self.server_service.get_all_servers()
        
        # is_monitoring_enabled가 True인 서버만 필터링
        enabled_servers = [
            s for s in servers 
            if s.get('is_monitoring_enabled', True)
        ]
        
        for server in enabled_servers:
            server_id = server['id']
            if server_id not in self.watchers:
                watcher = self._create_watcher(server)
                if watcher:
                    self.watchers[server_id] = watcher
                    # 초기 상태 캐시
                    self.status_cache[server_id] = server.get('status', 'active')
        
        self._last_server_ids = set(s['id'] for s in enabled_servers)
    
    def _create_watcher(self, server_data: Dict) -> Optional[BaseWatcher]:
        """서버 데이터로부터 Watcher 인스턴스 생성"""
        server_type = server_data.get('server_type')
        
        try:
            if server_type == 'web':
                config = WebConfig(
                    name=server_data.get('name'),
                    endpoint=f"{server_data.get('url', '')}{server_data.get('endpoint', '')}",
                    latency=int(server_data.get('latency', 30)),
                    auth_key=server_data.get('auth_key')
                )
                return WebWatcher(config)
            
            elif server_type == 'db':
                config = DBConfig(
                    name=server_data.get('name'),
                    host=server_data.get('HOST', server_data.get('host', 'localhost')),
                    port=int(server_data.get('PORT', server_data.get('port', 5432))),
                    username=server_data.get('USERNAME', server_data.get('username', '')),
                    password=server_data.get('PASSWORD', server_data.get('password', '')),
                    dbms=server_data.get('DBMS', server_data.get('dbms', 'postgresql')),
                    db_name=server_data.get('DB_NAME', server_data.get('db_name', ''))
                )
                return DBWatcher(config)
            
        except Exception as e:
            print(f"Failed to create watcher for {server_data.get('name')}: {e}")
            return None
        
        return None
    
    async def _monitor_loop(self):
        """메인 모니터링 루프"""
        while self.is_running:
            try:
                # 서버 목록 동기화
                await self._sync_servers()
                
                # Watchers의 스냅샷 획득 (동기화 이슈 방지)
                async with self.watchers_lock:
                    current_watchers = dict(self.watchers)
                
                # 스냅샷으로 체크 수행 (Lock 없이)
                tasks = [
                    self._check_server(server_id, watcher)
                    for server_id, watcher in current_watchers.items()
                ]
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # 조건부 저장
                await self._conditional_save()
                
                # 다음 체크까지 대기
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitor loop error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _sync_servers(self):
        """서버 목록 동기화 (안전하게)"""
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
                print(f"Server {server_id} removed from monitoring")
            
            # 새로 추가된 서버 또는 활성화된 서버 등록
            for server in enabled_servers:
                server_id = server['id']
                if server_id not in new_watchers:
                    watcher = self._create_watcher(server)
                    if watcher:
                        new_watchers[server_id] = watcher
                        self.status_cache[server_id] = server.get('status', 'active')
                        print(f"Server {server_id} ({server.get('name')}) added to monitoring")
            
            # 원자적으로 교체
            self.watchers = new_watchers
            self._last_server_ids = current_ids
    
    async def _check_server(self, server_id: str, watcher: BaseWatcher) -> Tuple[str, Optional[any]]:
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
                self.status_cache[server_id] = new_status
                self.dirty_servers.add(server_id)
                print(f"Server {server_id} status changed: {old_status} -> {new_status}")
            
            return (server_id, result)
            
        except Exception as e:
            print(f"Error checking server {server_id}: {e}")
            return (server_id, None)
    
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
        
        for server_id in dirty_copy:
            status = self.status_cache.get(server_id)
            if status:
                try:
                    self.server_service.update_server(server_id, {"status": status})
                except Exception as e:
                    print(f"Failed to save status for {server_id}: {e}")
        
        self.dirty_servers.clear()
        self.last_save_time = time.time()
        print(f"States saved to file ({len(dirty_copy)} servers)")
    
    def get_status(self) -> Dict:
        """현재 모니터링 상태 반환"""
        return {
            "is_running": self.is_running,
            "monitored_servers": len(self.watchers),
            "dirty_servers": len(self.dirty_servers),
            "last_save": self.last_save_time,
        }
