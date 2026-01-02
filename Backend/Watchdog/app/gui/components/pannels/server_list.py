import flet as ft
import sys
from pathlib import Path

# 부모 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from styles.text import main_pannel_title
from components.server_list import ServerListItem
from services import ServerService, MonitorService
from utils.notification_helper import NotificationHelper


class ServerListView:
    """서버 목록 뷰 클래스"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.server_service = ServerService()
        self.monitor_service = MonitorService()
        self.server_list_container: ft.Column
        self.server_items = {}  # server_id -> ServerListItem 매핑
        self._initialize_components()
        
        # 모니터링 상태 변경 리스너 등록
        self.monitor_service.add_listener(self._on_server_status_changed)
    
    def _initialize_components(self):
        """컴포넌트 초기화"""
        self.server_list_container = ft.Column(
            controls=[],
            spacing=10,
        )
    
    def _load_servers(self):
        """서버 데이터 로드 (ServerService에서 가져옴)"""
        self._update_server_list()
    
    def _handle_edit(self, server_data):
        """서버 수정 핸들러"""
        def handler(e):
            print(f"Edit server: {server_data['name']}")
            # TODO: 수정 다이얼로그 표시
        return handler
    
    def _handle_delete(self, server_data):
        """서버 삭제 핸들러"""
        def handler(e):
            print(f"Delete server: {server_data['name']}")
            # TODO: 삭제 확인 다이얼로그 표시
            success = self._remove_server(server_data['id'])
            
            # 알림 표시
            if self.page:
                if success:
                    NotificationHelper.success(
                        self.page, 
                        f"'{server_data['name']}' 서버가 삭제되었습니다"
                    )
                else:
                    NotificationHelper.error(
                        self.page, 
                        "서버 삭제에 실패했습니다"
                    )
        return handler
    
    def _handle_toggle_monitoring(self, server_data):
        """모니터링 토글 핸들러"""
        def handler(e):
            new_state = e.control.value
            server_id = server_data['id']
            
            # ServerService를 통해 is_monitoring_enabled 업데이트
            self.server_service.update_server(server_id, {
                "is_monitoring_enabled": new_state
            })
            
            status_text = "활성화" if new_state else "비활성화"
            print(f"Server {server_data['name']} monitoring {status_text}")
        
        return handler
    
    def _on_server_status_changed(self, server_id: str, status: str):
        """서버 상태 변경 이벤트 핸들러"""
        if server_id in self.server_items:
            item = self.server_items[server_id]
            item.update_status(status)
            
            # 알림 표시
            if self.page:
                server_name = item.name
                if status == "active":
                    NotificationHelper.success(self.page, f"'{server_name}' 서버가 정상 상태로 복구되었습니다.")
                elif status == "inactive":
                    NotificationHelper.error(self.page, f"'{server_name}' 서버 연결이 끊어졌습니다.")
                elif status == "warning":
                    NotificationHelper.warning(self.page, f"'{server_name}' 서버 응답이 지연되고 있습니다.")
                else:
                    NotificationHelper.info(self.page, f"'{server_name}' 서버 상태가 '{status}'(으)로 변경되었습니다.")

    def _remove_server(self, server_id: str):
        """서버 제거"""
        success = self.server_service.delete_server(server_id)
        if success:
            self._update_server_list()
    
    def _update_server_list(self):
        """서버 리스트 UI 업데이트"""
        self.server_list_container.controls.clear()
        self.server_items.clear()
        
        # ServerService에서 서버 목록 가져오기
        servers = self.server_service.get_all_servers()
        
        if not servers:
            self.server_list_container.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                icon=ft.Icons.INBOX,
                                size=48,
                                color="#9CA3AF"
                            ),
                            ft.Text(
                                "등록된 서버가 없습니다.",
                                size=14,
                                color="#6B7280"
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=40,
                    alignment=ft.Alignment(0,0),
                )
            )
        else:
            for server_data in servers:
                item = ServerListItem(
                    server_type=server_data["server_type"],
                    name=server_data["name"],
                    status=server_data.get("status", "active"),
                    url=server_data.get("url"),
                    host=server_data.get("host"),
                    port=server_data.get("port"),
                    dbms=server_data.get("dbms"),
                    on_edit=self._handle_edit(server_data),
                    on_delete=self._handle_delete(server_data),
                    is_monitoring_enabled=server_data.get("is_monitoring_enabled", True),
                    on_toggle_monitoring=self._handle_toggle_monitoring(server_data),
                )
                self.server_items[server_data['id']] = item
                self.server_list_container.controls.append(item.build())
        
        # 페이지에 추가된 경우에만 update 호출
        try:
            self.server_list_container.update()
        except RuntimeError:
            # 아직 페이지에 추가되지 않은 경우 무시
            pass
    
    def refresh(self):
        """서버 목록 새로고침"""
        self._update_server_list()
    
    def build(self) -> ft.Column:
        """뷰 빌드"""
        # 서버 데이터 로드
        self._load_servers()
        
        # 타이틀과 새로고침 버튼을 포함하는 Row
        title_row = ft.Row(
            controls=[
                main_pannel_title("서버 목록보기"),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_size=20,
                    tooltip="새로고침",
                    on_click=lambda e: self.refresh(),
                    icon_color="#4F46E5",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        return ft.Column([
            title_row,
            ft.Divider(height=15),
            ft.Text("등록된 서버 목록을 확인할 수 있습니다.", size=14, color="#718096"),
            ft.Container(height=10),
            self.server_list_container,
        ], expand=True, align=ft.Alignment(0, -1), scroll=ft.ScrollMode.AUTO)


# # 뷰 인스턴스 생성 및 export
# _server_list_view_instance = ServerListView()
# server_list_view = _server_list_view_instance.build()
# server_list_view_instance = _server_list_view_instance  # 인스턴스 접근용