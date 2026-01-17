from typing import List, Dict, Any, Callable, Optional
from app.utils.server_logger import LogEntry
from app.core.models import Status

class AppState:
    """중앙 상태 관리 클래스"""
    
    def __init__(self):
        self._servers: Dict[str, Any] = {}
        self._logs: List[LogEntry] = []
        self._listeners: List[Callable[[str, Any], None]] = []
        
    def add_listener(self, listener: Callable[[str, Any], None]):
        """상태 변경 이벤트를 수신할 리스너 등록"""
        if listener not in self._listeners:
            self._listeners.append(listener)
        
    def remove_listener(self, listener: Callable[[str, Any], None]):
        """리스너 제거"""
        if listener in self._listeners:
            self._listeners.remove(listener)
            
    def notify(self, event_type: str, data: Any = None):
        """리스너들에게 이벤트 알림"""
        for listener in self._listeners:
            try:
                listener(event_type, data)
            except Exception as e:
                print(f"Error in listener: {e}")
            
    # Server State Management
    def set_servers(self, servers: Dict[str, Any]):
        """서버 목록 전체 설정"""
        self._servers = servers
        self.notify("servers_loaded", self._servers)

    def update_server(self, server_id: str, data: Dict[str, Any]):
        """특정 서버 정보 업데이트"""
        if server_id in self._servers:
            self._servers[server_id].update(data)
            self.notify("server_updated", self._servers[server_id])
        else:
            # 서버가 없으면 추가 로직을 탈 수도 있으나, 여기서는 업데이트만 처리
            pass
            
    def add_server(self, server_data: Dict[str, Any]):
        """서버 추가"""
        server_id = server_data.get('id')
        if server_id:
            self._servers[server_id] = server_data
            self.notify("server_added", server_data)
        
    def remove_server(self, server_id: str):
        """서버 제거"""
        if server_id in self._servers:
            removed = self._servers.pop(server_id)
            self.notify("server_removed", removed)
            
    def get_servers(self) -> Dict[str, Any]:
        """현재 서버 목록 반환"""
        return self._servers
    
    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        return self._servers.get(server_id)
        
    # Log State Management
    def add_log(self, log_entry: LogEntry):
        """로그 추가"""
        self._logs.append(log_entry)
        # 메모리 관리를 위해 너무 많은 로그는 오래된 것부터 삭제 (예: 1000개)
        if len(self._logs) > 1000:
            self._logs.pop(0)
        self.notify("new_log", log_entry)
        
    def get_logs(self) -> List[LogEntry]:
        """전체 로그 반환"""
        return self._logs
    
    def clear_logs(self):
        """로그 초기화"""
        self._logs.clear()
        self.notify("logs_cleared")
