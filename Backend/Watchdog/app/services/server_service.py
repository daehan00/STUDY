import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import SERVERS_DATA_FILE, DATA_VERSION, SERVER_STATUS


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
        self._ensure_data_file()
        self.load()
        self._initialized = True
    
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
            print(f"데이터 로드 오류: {e}")
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
            print(f"데이터 저장 오류: {e}")
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
    
    def add_server(self, server_data: Dict) -> Dict:
        """새 서버 추가"""
        # ID와 타임스탬프 자동 생성
        new_server = {
            "id": self._generate_id(),
            "created_at": self._get_timestamp(),
            "updated_at": self._get_timestamp(),
            "status": SERVER_STATUS["ACTIVE"],  # 기본 상태
            **server_data
        }
        
        self.servers.append(new_server)
        self.save()
        
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
                return self.servers[i].copy()
        
        return None
    
    def delete_server(self, server_id: str) -> bool:
        """서버 삭제"""
        initial_length = len(self.servers)
        self.servers = [s for s in self.servers if s.get("id") != server_id]
        
        if len(self.servers) < initial_length:
            self.save()
            return True
        
        return False
    
    def get_servers_by_type(self, server_type: str) -> List[Dict]:
        """타입별로 서버 목록 조회"""
        return [s.copy() for s in self.servers if s.get("server_type") == server_type]
    
    def get_servers_by_status(self, status: str) -> List[Dict]:
        """상태별로 서버 목록 조회"""
        return [s.copy() for s in self.servers if s.get("status") == status]
