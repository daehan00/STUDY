import flet as ft

from components.pannels.server_add import server_add_view
from components.pannels.server_list import server_list_view, server_list_view_instance
from components.pannels.notifications import notification_settings_view

class MainPanel:
    def __init__(self, page: ft.Page):
        self.page = page
        self.container = None
        
    def build(self):
        self.container = ft.Container(
            content=self._get_home_view(),
            expand=True,
            bgcolor="#ffffff",
            padding=20,
        )
        return self.container
    
    def _get_home_view(self):
        """홈 화면"""
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.MONITOR_HEART, size=80, color="#cbd5e0"),
                    ft.Text(
                        " Watchdog",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#2d3748"
                    ),
                    ft.Text(
                        "좌측 메뉴에서 기능을 선택하세요",
                        size=14,
                        color="#718096"
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                alignment=ft.alignment.Alignment(0,0),
                expand=True
            )
        ], expand=True, align=ft.Alignment(0,-1), scroll=ft.ScrollMode.AUTO)
    
    def _get_add_server_view(self):
        """서버 추가하기 화면"""
        return server_add_view
    
    def _get_server_list_view(self):
        """서버 목록보기 화면"""
        # 뷰 전환 시 서버 목록 새로고침
        server_list_view_instance.refresh()
        return server_list_view
    
    def _get_notification_settings_view(self):
        """알림 채널 설정 화면"""
        return notification_settings_view
    
    def update_content(self, view_name: str):
        """메뉴 선택에 따라 콘텐츠 업데이트"""
        view_map = {
            "home": self._get_home_view,
            "add_server": self._get_add_server_view,
            "server_list": self._get_server_list_view,
            "notification_settings": self._get_notification_settings_view,
        }
        
        if view_name in view_map and self.container:
            self.container.content = view_map[view_name]()
            self.page.update()
