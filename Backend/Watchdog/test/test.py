import sys
import logging
from pathlib import Path
import flet as ft


# 프로젝트 루트 경로 설정
# PyInstaller 등으로 패키징 시 실행 경로가 달라질 수 있음을 고려
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent.parent
else:
    BASE_DIR = Path(__file__).parent.parent

sys.path.append(str(BASE_DIR))

from app.gui.main import main as gui_main
from app.config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

if __name__ == "__main__":
    # from app.services.monitor_service import MonitorService
    # from app.core.logger import log_manager
    # s = MonitorService()

    # print(log_manager.get_all_logs())

    ft.run(gui_main)
    