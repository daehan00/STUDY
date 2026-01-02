"""
애플리케이션 설정 파일
"""
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent.parent
APP_ROOT = Path(__file__).parent.parent

# 데이터 파일 설정
# 설치형 프로그램을 위해 사용자 홈 디렉토리에 데이터 저장
USER_DATA_DIR = Path.home() / ".watchdog"
DATA_DIR = USER_DATA_DIR / "data"
SERVERS_DATA_FILE = DATA_DIR / "servers.json"
DATA_VERSION = "1.0"

# 서버 상태 상수
SERVER_STATUS = {
    "ACTIVE": "active",
    "INACTIVE": "inactive",
    "WARNING": "warning"
}

# 서버 타입 상수
SERVER_TYPES = {
    "WEB": "web",
    "DATABASE": "db"
}

# DBMS 기본 포트
DBMS_PORTS = {
    "mysql": "3306",
    "postgresql": "5432",
}

# GUI 설정
GUI_COLORS = {
    "ERROR_RED": "#EF4444",
    "SUCCESS_GREEN": "#10B981",
    "WARNING_ORANGE": "#F59E0B",
    "GRAY": "#6B7280",
}
