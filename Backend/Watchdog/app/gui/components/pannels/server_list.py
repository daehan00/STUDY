import flet as ft
import logging

from app.gui.styles.text import main_pannel_title
from app.gui.components.server_list import ServerListItem
from app.gui.components.popup import create_edit_popup
from app.gui.utils.notification_helper import NotificationHelper
from app.services import ServerService, MonitorService
from app.state.app_state import AppState

logger = logging.getLogger("ServerListView")


class ServerListView:
    """서버 목록 뷰 클래스"""
    
    def __init__(self, page: ft.Page, app_state: AppState):
        self.page = page
        self.app_state = app_state
        self.server_service = ServerService()
        self.monitor_service = MonitorService()
        self.server_list_container: ft.Column = ft.Column(controls=[], spacing=10)
        self.server_items = {}  # server_id -> ServerListItem 매핑
        
        # AppState 변경 리스너 등록
        self.app_state.add_listener(self._on_state_change)
        
    def _on_state_change(self, event_type: str, data):
        """앱 상태 변경 핸들러"""
        if event_type in ["servers_loaded", "server_added", "server_removed"]:
            self._update_server_list()
        elif event_type == "server_updated":
            self._update_single_server(data)
            
    def _update_single_server(self, server_data):
        """단일 서버 아이템만 업데이트 (화면 깜빡임 방지 & 알림 처리)"""
        server_id = server_data['id']
        
        if server_id in self.server_items:
            item_control = self.server_items[server_id]
            
            # 상태 변경 감지 및 알림
            old_status = getattr(item_control, "status", None)
            new_status = server_data.get("status")
            
            if old_status != new_status:
                self._show_status_notification(server_data['name'], new_status)
            
            # 아이템 UI 업데이트
            # ServerListItem에 update 메서드가 있다고 가정하거나, 새로 그려서 교체
            # 여기서는 간단히 리스트 전체 갱신 대신 해당 아이템만 갱신하는 로직이 필요하지만
            # ServerListItem 구조를 정확히 모르므로, 안전하게 전체 갱신을 하거나
            # ServerListItem이 상태를 받아 스스로 갱신하도록 설계되어 있는지 확인 필요.
            # 일단 안전하게 전체 리트스 업데이트 호출 (최적화는 추후)
            # self._update_server_list() # 너무 잦은 갱신일 수 있음.
            

            # 아이템 UI 업데이트
            if hasattr(item_control, 'update_data'):
                item_control.update_data(server_data)
            else:
                # update_data가 없으면 리스트 전체 갱신
                self._update_server_list()
        else:
            # 리스트에 없는 항목이면 전체 갱신
            self._update_server_list()

    def _show_status_notification(self, server_name: str, status: str):
        """상태 변경 알림 표시"""
        if not self.page:
            return
            
        if status == "active":
            NotificationHelper.success(self.page, f"'{server_name}' 서버가 정상 상태로 복구되었습니다.")
        elif status == "inactive":
            NotificationHelper.error(self.page, f"'{server_name}' 서버 연결이 끊어졌습니다.")
        elif status == "warning":
            NotificationHelper.warning(self.page, f"'{server_name}' 서버 응답이 지연되고 있습니다.")

    def _update_server_list(self):
        """서버 목록 UI 갱신"""
        servers = self.app_state.get_servers().values()
        
        self.server_items.clear()
        self.server_list_container.controls.clear()
        
        if not servers:
            self.server_list_container.controls.append(
                ft.Text("등록된 서버가 없습니다.", color="#a0aec0")
            )
        else:
            for server in servers:
                # ServerListItem 생성
                item = ServerListItem(
                    server_type=server.get("server_type"),
                    name=server.get("name"),
                    status=server.get("status", "active"),
                    url=server.get("url"),
                    host=server.get("host"),
                    port=server.get("port"),
                    dbms=server.get("dbms"),
                    on_edit=self._handle_edit(server),
                    on_delete=self._handle_delete(server),
                    is_monitoring_enabled=server.get("is_monitoring_enabled", True),
                    on_toggle_monitoring=self._handle_toggle_monitoring(server)
                )
                self.server_items[server['id']] = item
                self.server_list_container.controls.append(item.build())
        
        try:
            if self.page:
                self.server_list_container.update()
        except RuntimeError:
            pass


    def _handle_edit(self, server_data):
        """서버 수정 핸들러"""
        def handler(e):
            logger.debug(f"Edit handler called for {server_data.get('name')}")
            
            def on_save(updated_data):
                logger.info(f"Saving data: {updated_data}")
                # 서버 정보 업데이트
                self.server_service.update_server(server_data['id'], updated_data)
                
                # UI 업데이트
                self._update_server_list()
                
                # 팝업 닫기
                self.page.pop_dialog()
                self.page.update()
                
                # 알림
                NotificationHelper.success(self.page, f"'{updated_data['name']}' 서버 정보가 수정되었습니다.")

            def on_cancel(e):
                logger.debug("Cancel clicked")
                self.page.pop_dialog()

            # 팝업 생성 및 표시
            logger.debug("Creating popup")
            popup = create_edit_popup(
                server_data=server_data,
                on_save=on_save,
                on_cancel=on_cancel
            )
            
            self.page.show_dialog(popup)
            popup.open = True
            self.page.update()
            
        return handler
    
    def _handle_delete(self, server_data):
        """서버 삭제 핸들러"""
        def handler(e):
            logger.info(f"Delete server: {server_data['name']}")
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
            logger.info(f"Server {server_data['name']} monitoring {status_text}")
        
        return handler
    
    def _remove_server(self, server_id: str):
        """서버 제거"""
        success = self.server_service.delete_server(server_id)
        if success:
            self._update_server_list()
    
    def refresh(self):
        """서버 목록 새로고침"""
        self._update_server_list()
    
    def build(self) -> ft.Column:
        """뷰 빌드"""
        
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