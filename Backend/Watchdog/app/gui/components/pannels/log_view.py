# app/gui/components/pannels/log_view.py

import flet as ft
from datetime import datetime
from app.utils.server_logger import LogEntry
from app.core.models import MessageGrade
from app.state.app_state import AppState

class LogView(ft.Container):
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.log_list = ft.ListView(
            expand=True,
            spacing=2,
            auto_scroll=True,  # 새 로그가 오면 자동으로 맨 아래로 스크롤
            padding=10,
        )
        
        # 스타일링: 터미널 느낌 (검은 배경, 모노스페이스 폰트)
        self.content = ft.Container(
            content=self.log_list,
            bgcolor="#1e1e1e",  # VS Code 터미널 색상
            border_radius=5,
            border=ft.Border.all(1, "#333333"),
        )
        self.expand = True
        self.align=ft.Alignment(0,-1)
        self.scroll=ft.ScrollMode.AUTO
        
        # AppState에서 기존 로그 로드
        for log in self.app_state.get_logs():
            self._on_new_log(log)
            
        # AppState에 리스너 등록
        self.app_state.add_listener(self._on_state_change)

    def _on_state_change(self, event_type, data):
        if event_type == "new_log":
            self._on_new_log(data)

    def _get_color_by_grade(self, grade: MessageGrade) -> str:
        """로그 등급별 색상 지정"""
        if grade == MessageGrade.critical:
            return "#ff5252"  # Red
        elif grade == MessageGrade.warning:
            return "#ffab40"  # Orange
        elif grade == MessageGrade.resolved:
            return "#69f0ae"  # Green
        elif grade == MessageGrade.start:
            return "#448aff"  # Blue
        elif grade == MessageGrade.stop:
            return "#7c4dff"  # Purple
        else:
            return "#e0e0e0"  # White/Gray

    def _on_new_log(self, log: LogEntry):
        """새 로그가 들어오면 호출되는 콜백"""
        
        # 타임스탬프 포맷팅 (HH:MM:SS)
        try:
            ts = datetime.fromisoformat(log.timestamp).strftime("%H:%M:%S")
        except:
            ts = log.timestamp

        # 로그 텍스트 구성
        log_line = ft.Row(
            controls=[
                ft.Text(f"[{ts}]", color="#808080", size=12, font_family="Consolas"),
                ft.Text(f"[{log.source}]", color="#4ec9b0", size=12, weight=ft.FontWeight.BOLD, font_family="Consolas"),
                ft.Text(log.details if isinstance(log.details, str) else str(log.details), 
                        color=self._get_color_by_grade(log.event), 
                        size=12, 
                        font_family="Consolas",
                        selectable=True, # 텍스트 복사 가능하게
                        expand=True) # 긴 내용은 줄바꿈
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=5,
        )

        # UI 업데이트 (Main Thread 안전하게 처리)
        self.log_list.controls.append(log_line)
        
        # 로그가 너무 많이 쌓이면 앞부분 제거 (메모리 관리)
        if len(self.log_list.controls) > 200:
            self.log_list.controls.pop(0)
            
        try:
            if self.page:
                self.update()
        except RuntimeError:
            pass