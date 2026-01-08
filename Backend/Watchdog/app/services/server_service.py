import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.config import SERVERS_DATA_FILE, DATA_VERSION, SERVER_STATUS

logger = logging.getLogger("ServerService")


class ServerService:
    """서버 데이터 관리 서비스 (Singleton)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # config에서 데이터 파일 경로 가져오기
        self.data_file = SERVERS_DATA_FILE
        self.data_version = DATA_VERSION
        
        self.servers: List[Dict] = []
        self.listeners = []  # 리스너 목록
        self._ensure_data_file()
        self.load()
        self._initialized = True
    
    def add_listener(self, callback):
        """데이터 변경 리스너 추가"""
        if callback not in self.listeners:
            self.listeners.append(callback)
            
    def _notify_listeners(self, event_type: str, server_data: Dict):
        """리스너들에게 변경 알림"""
        for listener in self.listeners:
            try:
                listener(event_type, server_data)
            except Exception as e:
                logger.error(f"Error in server service listener: {e}")

    def _ensure_data_file(self) -> None:
        """데이터 파일이 존재하는지 확인하고 없으면 생성"""
        if not self.data_file.exists():
            # 디렉토리가 없으면 생성
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 초기 데이터 구조 생성
            initial_data = {
                "version": self.data_version,
                "servers": []
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
    
    def load(self) -> None:
        """JSON 파일에서 서버 데이터 로드"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.servers = data.get("servers", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"데이터 로드 오류: {e}")
            self.servers = []
    
    def save(self) -> None:
        """현재 서버 데이터를 JSON 파일에 저장"""
        data = {
            "version": self.data_version,
            "servers": self.servers
        }
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"데이터 저장 오류: {e}")
            raise
    
    def _generate_id(self) -> str:
        """고유한 UUID 생성"""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> str:
        """현재 시간을 ISO 형식으로 반환"""
        return datetime.now().isoformat()
    
    def get_all_servers(self) -> List[Dict]:
        """모든 서버 목록 반환"""
        return self.servers.copy()
    
    def get_server_by_id(self, server_id: str) -> Optional[Dict]:
        """ID로 특정 서버 조회"""
        for server in self.servers:
            if server.get("id") == server_id:
                return server.copy()
        return None
    
    def _check_duplicate(self, server_data: Dict) -> Optional[Dict]:
        """중복 서버 검사"""
        server_type = server_data.get('server_type')
        
        for server in self.servers:
            if server.get('server_type') != server_type:
                continue
            
            # Web 서버: URL + Endpoint로 비교
            if server_type == 'web':
                if (server.get('url') == server_data.get('url') and 
                    server.get('endpoint') == server_data.get('endpoint')):
                    return server
            
            # DB 서버: Host + Port + DB_NAME으로 비교
            elif server_type == 'db':
                if (server.get('DBMS') == server_data.get('dbms') and
                    server.get('HOST') == server_data.get('host') and 
                    server.get('PORT') == server_data.get('port') and
                    server.get('DB_NAME') == server_data.get('db_name')):
                    return server
        
        return None
    
    def add_server(self, server_data: Dict) -> Dict:
        """새 서버 추가"""
        # 중복 검사
        duplicate = self._check_duplicate(server_data)
        if duplicate:
            raise ValueError(f"동일한 서버가 이미 존재합니다: {duplicate.get('name', 'Unknown')}")
        
        # ID와 타임스탬프 자동 생성
        new_server = {
            "id": self._generate_id(),
            "created_at": self._get_timestamp(),
            "updated_at": self._get_timestamp(),
            "status": SERVER_STATUS["ACTIVE"],  # 기본 상태
            "is_monitoring_enabled": True,  # 기본값: 모니터링 활성화
            **server_data
        }
        
        self.servers.append(new_server)
        self.save()
        
        self._notify_listeners("add", new_server)
        return new_server.copy()
    
    def update_server(self, server_id: str, updates: Dict) -> Optional[Dict]:
        """서버 정보 업데이트"""
        for i, server in enumerate(self.servers):
            if server.get("id") == server_id:
                # 기존 데이터 업데이트
                self.servers[i].update(updates)
                # updated_at 갱신
                self.servers[i]["updated_at"] = self._get_timestamp()
                
                self.save()
                
                updated_server = self.servers[i].copy()
                self._notify_listeners("update", updated_server)
                return updated_server
        
        return None
    
    def delete_server(self, server_id: str) -> bool:
        """서버 삭제"""
        initial_length = len(self.servers)
        deleted_server = next((s for s in self.servers if s.get("id") == server_id), None)
        self.servers = [s for s in self.servers if s.get("id") != server_id]
        
        if len(self.servers) < initial_length:
            self.save()
            if deleted_server:
                self._notify_listeners("delete", deleted_server)
            return True
        
        return False
    
    def get_servers_by_type(self, server_type: str) -> List[Dict]:
        """타입별로 서버 목록 조회"""
        return [s.copy() for s in self.servers if s.get("server_type") == server_type]
    
    def get_servers_by_status(self, status: str) -> List[Dict]:
        """상태별로 서버 목록 조회"""
        return [s.copy() for s in self.servers if s.get("status") == status]
