import sys
from pathlib import Path
import flet as ft

# 프로젝트 루트 경로 설정
# PyInstaller 등으로 패키징 시 실행 경로가 달라질 수 있음을 고려
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

from app.gui.main import main as gui_main

if __name__ == "__main__":
    # Flet 앱 실행
    ft.run(gui_main)
