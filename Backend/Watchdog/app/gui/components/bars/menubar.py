import flet as ft
import asyncio

from app.services import MonitorService
from app.gui.utils.notification_helper import NotificationHelper


class MenuBar:
    """상단 메뉴바 클래스"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.monitor_service = MonitorService()
        self.is_monitoring = False
        self.play_button = None
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
            print("✅ Monitoring started successfully")
            
        except ValueError as ve:
            # 서버 0개 에러
            NotificationHelper.warning(self.page, str(ve), duration=4000)
            print(f"⚠️  {ve}")
        except Exception as ex:
            # 기타 에러
            NotificationHelper.error(self.page, f"모니터링 시작 실패: {str(ex)}")
    
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
            
            print("✅ Monitoring stopped successfully")
        except Exception as ex:
            NotificationHelper.error(self.page, f"모니터링 중지 실패: {str(ex)}")
    
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
                    padding=ft.Padding.only(right=15, left=80)
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
                            on_click=lambda _: print("설정"),
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
def create_menubar(page: ft.Page):
    """MenuBar 인스턴스 생성 및 빌드"""
    menubar = MenuBar(page)
    return menubar.build()