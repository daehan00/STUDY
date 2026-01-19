import flet as ft
import asyncio
import logging

from app.services import MonitorService
from app.gui.utils.notification_helper import NotificationHelper
from app.config.user_config import user_setting

logger = logging.getLogger("MenuBar")


class MenuBar:
    """상단 메뉴바 클래스"""
    
    def __init__(self, page: ft.Page, handler):
        self.page = page
        self.monitor_service = MonitorService()
        self.is_monitoring = False
        self.play_button: ft.Container
        self.handler = handler
        self._initialize_components()
    
    def _initialize_components(self):
        """컴포넌트 초기화"""
        self.play_button = ft.Container(
            content=ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=25, color="#10B981"),
            width=40,
            height=40,
            border_radius=5,
            alignment=ft.Alignment(0, 0),
            tooltip="모니터링 시작",
            ink=True,
            on_click=self._toggle_monitoring,
        )
    
    def _toggle_monitoring(self, e):
        """모니터링 시작/중지 토글"""
        if not self.is_monitoring:
            # 시작
            asyncio.create_task(self._start_monitoring())
        else:
            # 중지
            asyncio.create_task(self._stop_monitoring())
    
    async def _start_monitoring(self):
        """모니터링 시작"""
        try:
            await self.monitor_service.start()
            self.is_monitoring = True
            
            # 버튼 UI 변경 (중지 버튼으로)
            self.play_button.content = ft.Icon(ft.Icons.STOP, size=25, color="#EF4444")
            self.play_button.tooltip = "모니터링 중지"
            self.play_button.update()
            # 성공 알림
            NotificationHelper.success(self.page, "모니터링이 시작되었습니다")
            logger.info("✅ Monitoring started successfully")
            
        except ValueError as ve:
            # 서버 0개 에러
            NotificationHelper.warning(self.page, str(ve), duration=4000)
            logger.error(f"⚠️  {ve}")
        except Exception as ex:
            # 기타 에러
            NotificationHelper.error(self.page, f"모니터링 시작 실패: {str(ex)}")
            logger.error(f"모니터링 시작 실패: {str(ex)}")
    
    async def _stop_monitoring(self):
        """모니터링 중지"""
        try:
            await self.monitor_service.stop()
            self.is_monitoring = False
            NotificationHelper.info(self.page, "모니터링이 중지되었습니다")
            # 버튼 UI 변경 (실행 버튼으로)
            self.play_button.content = ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=25, color="#10B981")
            self.play_button.tooltip = "모니터링 시작"
            self.play_button.update()
            
            logger.info("✅ Monitoring stopped successfully")
        except Exception as ex:
            NotificationHelper.error(self.page, f"모니터링 중지 실패: {str(ex)}")
            logger.error(f"모니터링 중지 실패: {str(ex)}")

    def _open_settings_dialog(self, e):
        """설정 다이얼로그 열기"""
        
        # 현재 설정 값 로드
        current_config = user_setting.get_all()
        
        # UI 컨트롤 참조 변수
        theme_mode = ft.Dropdown(
            label="테마 설정",
            value=current_config.get("theme_mode", "light"),
            options=[
                ft.dropdown.Option("light", "라이트 모드"),
                ft.dropdown.Option("dark", "다크 모드"),
                ft.dropdown.Option("system", "시스템 설정"),
            ],
            width=200,
        )
        
        notifications_enabled = ft.Switch(
            # label="알림 활성화",
            value=current_config.get("notifications_enabled", True),
        )
        
        log_retention = ft.TextField(
            label="로그 보관 기간 (일)",
            value=str(current_config.get("log_retention_days", 7)),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
        )

        max_log = ft.TextField(
            label="로그 최대 개수",
            value=str(current_config.get("max_logs", 1000)),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
        )
        
        auto_start = ft.Switch(
            # label="앱 실행 시 자동 모니터링 시작",
            value=current_config.get("auto_start_monitoring", False),
        )

        def close_dlg(e):
            self.page.pop_dialog()

        def save_settings(e):
            """설정 저장 처리"""
            try:
                # 입력값 수집
                new_settings = {
                    "theme_mode": theme_mode.value,
                    "notifications_enabled": notifications_enabled.value,
                    "log_retention_days": int(log_retention.value) if log_retention.value.isdigit() else 7,
                    "auto_start_monitoring": auto_start.value,
                    "max_logs" : max_log.value
                }
                
                # 저장
                result = user_setting.update_all(new_settings)
                
                if result is None: # 성공 시 None 반환
                    NotificationHelper.success(self.page, "설정이 저장되었습니다.")
                else:
                    NotificationHelper.error(self.page, f"설정 저장 실패: {result}")
                
                self.page.pop_dialog()
                
            except Exception as ex:
                NotificationHelper.error(self.page, f"설정 저장 중 오류: {ex}")

        # 다이얼로그 구성
        dlg = ft.AlertDialog(
            title=ft.Text("환경 설정"),
            content=ft.Column([
                ft.Container(height=10),
                theme_mode,
                ft.Container(height=10),
                ft.Row(
                    [ft.Text("알림 활성화"), notifications_enabled],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=200
                ),
                ft.Container(height=10),
                ft.Column(
                    [
                        ft.Text("로그 설정"),
                        log_retention,
                        max_log,
                    ], width=200
                ),
                ft.Container(height=10),
                ft.Row(
                    [ft.Text("실행 시 모니터링 시작"), auto_start],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=200
                ),
                ft.Container(height=20),
            ], tight=True, width=250, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("취소", on_click=close_dlg),
                ft.ElevatedButton("저장", on_click=save_settings, bgcolor="#4F46E5", color="white"),
            ],
            alignment=ft.Alignment(0,0),
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.show_dialog(dlg)

    def build(self):
        """메뉴바 빌드"""
        top_menu = ft.Container(
            content=ft.Row([
                # 왼쪽: 타이틀 영역
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MONITOR_HEART, color="#ff6b35", size=24),
                        ft.Text("Watchdog", size=18, weight=ft.FontWeight.BOLD, color="#2d3748"),
                    ], spacing=10),
                    padding=ft.Padding.only(right=15, left=80),
                    on_click=self.handler,
                    on_hover=lambda e: setattr(e.control, "bgcolor", "#f3f4f6" if e.data == "true" else None) or e.control.update(),
                ),
                # 가운데: 검색창
                ft.Container(
                    content=ft.TextField(
                        hint_text="Search...",
                        border=ft.InputBorder.OUTLINE,
                        dense=True,
                        prefix_icon=ft.Icons.SEARCH,
                        width=350,
                        height=35,
                    ),
                    expand=True,
                    alignment=ft.alignment.Alignment(0, 0)
                ),
                # 오른쪽: 설정 및 알람 버튼
                ft.Container(
                    content=ft.Row([
                        self.play_button,
                        ft.Container(
                            content=ft.Icon(ft.Icons.SETTINGS, size=20),
                            width=40,
                            height=40,
                            border_radius=5,
                            alignment=ft.Alignment(0, 0),
                            tooltip="설정",
                            ink=True,
                            on_click=lambda _: self._open_settings_dialog("설정"),
                        ),
                        ft.Container(
                            content=ft.Icon(ft.Icons.NOTIFICATIONS, size=20),
                            width=40,
                            height=40,
                            border_radius=5,
                            alignment=ft.Alignment(0, 0),
                            tooltip="알림",
                            ink=True,
                            on_click=lambda _: print("알림"),
                        ),
                    ], spacing=5),
                    padding=ft.Padding.only(right=15)
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#ffffff",
            padding=ft.Padding.only(left=0, right=15, top=0, bottom=0),
            height=50
        )
        
        # 드래그 가능 영역 설정
        return ft.WindowDragArea(content=top_menu)


# 뷰 생성 함수 (하위 호환성)
def create_menubar(page: ft.Page, handler):
    """MenuBar 인스턴스 생성 및 빌드"""
    menubar = MenuBar(page, handler)
    return menubar.build()