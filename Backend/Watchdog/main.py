import sys
import logging
import flet as ft
from pathlib import Path

# 프로젝트 루트 경로 설정
# PyInstaller 등으로 패키징 시 실행 경로가 달라질 수 있음을 고려
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

from app.gui.main import main as gui_main
from app.config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

if __name__ == "__main__":
    # Flet 앱 실행
    ft.run(gui_main)
