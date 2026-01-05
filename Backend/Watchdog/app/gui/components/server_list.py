import flet as ft
from typing import Optional


class ServerListItem:
    """서버 리스트 아이템 컴포넌트"""
    
    def __init__(
        self,
        server_type: str,
        name: str,
        status: str = "active",
        is_monitoring_enabled: bool = True,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        dbms: Optional[str] = None,
        on_edit=None,
        on_delete=None,
        on_toggle_monitoring=None,
    ):
        self.server_type = server_type
        self.name = name
        self.status = status
        self.is_monitoring_enabled = is_monitoring_enabled
        self.url = url
        self.host = host
        self.port = port
        self.dbms = dbms
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle_monitoring = on_toggle_monitoring
    
    def _get_status_color(self) -> str:
        """상태에 따른 색상 반환"""
        status_colors = {
            "active": "#10B981",  # 녹색
            "inactive": "#EF4444",  # 빨간색
            "warning": "#F59E0B",  # 주황색
        }
        return status_colors.get(self.status, "#6B7280")
    
    def _get_status_text(self) -> str:
        """상태 텍스트 반환"""
        status_texts = {
            "active": "정상",
            "inactive": "중지",
            "warning": "경고",
        }
        return status_texts.get(self.status, "알 수 없음")
    
    def _build_server_info(self) -> list:
        """서버 정보 텍스트 생성"""
        info_parts = []
        
        if self.server_type == "web":
            if self.url:
                info_parts.append(f"URL: {self.url}")
            if self.port:
                info_parts.append(f"Port: {self.port}")
        elif self.server_type == "db":
            if self.dbms:
                info_parts.append(f"DBMS: {self.dbms.upper()}")
            if self.host:
                info_parts.append(f"Host: {self.host}")
            if self.port:
                info_parts.append(f"Port: {self.port}")
        
        return [
            ft.Text(
                " | ".join(info_parts) if info_parts else "정보 없음",
                size=12,
                color="#6B7280"
            )
        ]
    
    def update_status(self, new_status: str):
        """상태 업데이트"""
        self.status = new_status
        
        # 컨트롤이 페이지에 연결되어 있을 때만 업데이트
        if hasattr(self, 'status_text_control') and self.status_text_control.page:
            self.status_text_control.value = self._get_status_text()
            self.status_text_control.update()
            
        if hasattr(self, 'status_container_control') and self.status_container_control.page:
            self.status_container_control.bgcolor = self._get_status_color()
            self.status_container_control.update()

    def build(self) -> ft.Container:
        """리스트 아이템 UI 빌드"""
        self.status_text_control = ft.Text(
            self._get_status_text(),
            size=10,
            color="white",
            weight=ft.FontWeight.BOLD,
        )
        
        self.status_container_control = ft.Container(
            content=self.status_text_control,
            bgcolor=self._get_status_color(),
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            border_radius=12,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    # 서버 타입 아이콘
                    ft.Container(
                        content=ft.Icon(
                            icon=ft.Icons.WEB if self.server_type == "web" else ft.Icons.STORAGE,
                            size=24,
                            color="#4F46E5"
                        ),
                        width=40,
                    ),
                    # 서버 정보
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    self.status_container_control,
                                    ft.Text(
                                        self.name,
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1F2937"
                                    ),
                                ],
                                spacing=10,
                            ),
                            *self._build_server_info(),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Switch(
                        value=self.is_monitoring_enabled,
                        on_change=self.on_toggle_monitoring,
                        active_color="#10B981",
                        inactive_thumb_color="#EF4444",
                        tooltip="모니터링 활성화/비활성화",
                        scale=0.8,
                    ),
                    # 액션 버튼
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="수정",
                                on_click=self.on_edit,
                                icon_color="#6B7280",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=20,
                                tooltip="삭제",
                                on_click=self.on_delete,
                                icon_color="#EF4444",
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border=ft.Border.all(1, "#E5E7EB"),
            border_radius=8,
            bgcolor="white",
        )

