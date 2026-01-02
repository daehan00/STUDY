"""
알림 표시 헬퍼 유틸리티
커스텀 디자인의 SnackBar를 사용하여 화면 하단 중앙에 알림을 표시합니다.
"""

import flet as ft
from typing import Callable, Optional


class NotificationType:
    """알림 타입"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationHelper:
    """페이지에 커스텀 알림을 표시하는 헬퍼 클래스"""
    
    # 페이지별 현재 활성화된 SnackBar를 추적
    _active_snackbars = {}
    
    @staticmethod
    def show(
        page: ft.Page,
        message: str,
        notification_type: str = NotificationType.INFO,
        duration: int = 1000,
        action: Optional[str] = None,
        action_callback: Optional[Callable] = None,
    ):
        """
        커스텀 SnackBar 알림을 표시합니다.
        
        Args:
            page: Flet Page 객체
            message: 표시할 메시지
            notification_type: 알림 타입 (success, error, warning, info)
            duration: 표시 시간 (밀리초)
            action: 액션 버튼 텍스트 (선택사항)
            action_callback: 액션 버튼 클릭 시 실행할 함수 (선택사항)
        """
        # 타입별 색상 및 아이콘 설정
        type_config = {
            NotificationType.SUCCESS: {
                "bg_color": "#10B981",
                "icon": ft.Icons.CHECK_CIRCLE,
                "icon_color": "#FFFFFF",
            },
            NotificationType.ERROR: {
                "bg_color": "#EF4444",
                "icon": ft.Icons.ERROR,
                "icon_color": "#FFFFFF",
            },
            NotificationType.WARNING: {
                "bg_color": "#F59E0B",
                "icon": ft.Icons.WARNING,
                "icon_color": "#FFFFFF",
            },
            NotificationType.INFO: {
                "bg_color": "#3B82F6",
                "icon": ft.Icons.INFO,
                "icon_color": "#FFFFFF",
            },
        }
        
        config = type_config.get(notification_type, type_config[NotificationType.INFO])
        
        # 기존 SnackBar가 있으면 닫고 제거
        page_id = id(page)
        if page_id in NotificationHelper._active_snackbars:
            old_snackbar = NotificationHelper._active_snackbars[page_id]
            try:
                old_snackbar.open = False
                if old_snackbar in page.overlay:
                    page.overlay.remove(old_snackbar)
            except Exception:
                pass
        
        # 커스텀 컨텐츠 (카드 스타일)
        content_container = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(config["icon"], color=config["icon_color"], size=22),
                    ft.Text(
                        message, 
                        color="#FFFFFF", 
                        size=14, 
                        weight=ft.FontWeight.W_500,
                        no_wrap=False,
                        text_align=ft.TextAlign.CENTER,
                        # expand=True,
                    ),
                ], 
                spacing=12,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=config["bg_color"],
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, "#000000"),
                offset=ft.Offset(0, 4),
            ),
        )
        
        # SnackBar 생성 (투명 배경, 커스텀 컨텐츠 사용)
        snackbar = ft.SnackBar(
            content=content_container,
            bgcolor=ft.Colors.TRANSPARENT,  # 투명 배경
            duration=duration,
            action=action,
            on_action=action_callback,
            behavior=ft.SnackBarBehavior.FIXED,  # 떠있는 형태
            margin=ft.Margin.only(bottom=20, left=20, right=20),
            elevation=0,  # 기본 그림자 제거 (커스텀 그림자 사용)
        )
        
        # 페이지에 추가
        page.overlay.append(snackbar)
        snackbar.open = True
        
        # 현재 활성화된 SnackBar로 등록
        NotificationHelper._active_snackbars[page_id] = snackbar
        
        page.update()
    
    @staticmethod
    def success(page: ft.Page, message: str, duration: int = 1000):
        """성공 메시지 표시"""
        NotificationHelper.show(page, message, NotificationType.SUCCESS, duration)
    
    @staticmethod
    def error(page: ft.Page, message: str, duration: int = 1000):
        """에러 메시지 표시"""
        NotificationHelper.show(page, message, NotificationType.ERROR, duration)
    
    @staticmethod
    def warning(page: ft.Page, message: str, duration: int = 1000):
        """경고 메시지 표시"""
        NotificationHelper.show(page, message, NotificationType.WARNING, duration)
    
    @staticmethod
    def info(page: ft.Page, message: str, duration: int = 1000):
        """정보 메시지 표시"""
        NotificationHelper.show(page, message, NotificationType.INFO, duration)
