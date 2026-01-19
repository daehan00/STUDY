# app/gui/components/pannels/log_view.py

import flet as ft
from datetime import datetime
from app.utils.server_logger import LogEntry
from app.core.models import MessageGrade
from app.state.app_state import AppState
from app.config import GUI_COLORS

class LogView(ft.Container):
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        
        # 로그 리스트 (가로/세로 스크롤 지원)
        self.log_list = ft.Column(
            expand=True,
            spacing=2,
            auto_scroll=True,  # 새 로그가 오면 자동으로 맨 아래로 스크롤
            scroll=ft.ScrollMode.AUTO,
        )
        
        # LogView(Container) 스타일링 및 설정
        self.expand = True
        self.bgcolor = "#1e1e1e"  # VS Code 터미널 색상
        self.border_radius = 5
        self.border = ft.Border.all(1, "#333333")
        self.padding = 10
        self.alignment = ft.Alignment(-1,-1)
        
        # 내부 컨텐츠 설정
        self.content = self.log_list
        
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
            return GUI_COLORS["ERROR_RED"]
        elif grade == MessageGrade.warning:
            return GUI_COLORS["WARNING_ORANGE"]
        elif grade == MessageGrade.resolved:
            return GUI_COLORS["SUCCESS_GREEN"]
        elif grade == MessageGrade.start:
            return GUI_COLORS["START"]
        elif grade == MessageGrade.stop:
            return GUI_COLORS["STOP"]
        else:
            return GUI_COLORS["ETC"]

    def _on_new_log(self, log: LogEntry):
        """새 로그가 들어오면 호출되는 콜백"""
        
        # 타임스탬프 포맷팅 (HH:MM:SS)
        try:
            ts = datetime.fromisoformat(log.timestamp).strftime("%d/%m, %H:%M:%S")
        except:
            ts = log.timestamp

        # 로그 텍스트 구성
        log_line = ft.Row(
            controls=[
                ft.Text(f"[{ts}]", color="#808080", size=12, font_family="Consolas", width=105, selectable=True),
                ft.Text(
                    f"[{log.source}]".ljust(20), color="#4ec9b0", size=12,
                    weight=ft.FontWeight.BOLD, font_family="Consolas", width=125, selectable=True,
                    expand=False, overflow=ft.TextOverflow.VISIBLE, text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    log.event.name.upper(), color=self._get_color_by_grade(log.event), size=12,
                    weight=ft.FontWeight.BOLD, font_family="Consolas", width=80, selectable=True,
                    expand=False, text_align=ft.TextAlign.CENTER
                ),
                ft.Text(log.details if isinstance(log.details, str) else f"message: {str(log.details.get("message", "-") or log.details.get("error_message", "-"))}", 
                        color=self._get_color_by_grade(log.event), 
                        size=12, 
                        font_family="Consolas",
                        selectable=True, # 텍스트 복사 가능하게
                        expand=False)
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=5,
        )
        log_line.scroll = ft.ScrollMode.AUTO

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
