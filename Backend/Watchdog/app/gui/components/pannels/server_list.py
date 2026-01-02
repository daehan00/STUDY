import flet as ft

from styles.text import main_pannel_title
from components.server_list import ServerListItem


class ServerListView:
    """서버 목록 뷰 클래스"""
    
    def __init__(self):
        self.server_list_container: ft.Column
        self.servers = []
        self._initialize_components()
    
    def _initialize_components(self):
        """컴포넌트 초기화"""
        self.server_list_container = ft.Column(
            controls=[],
            spacing=10,
        )
    
    def _load_sample_data(self):
        """샘플 데이터 로드 (실제로는 DB나 API에서 가져옴)"""
        self.servers = [
            {
                "server_type": "web",
                "name": "메인 웹서버",
                "status": "active",
                "url": "https://example.com",
                "port": "443",
            },
            {
                "server_type": "web",
                "name": "API 서버",
                "status": "warning",
                "url": "https://api.example.com",
                "port": "8080",
            },
            {
                "server_type": "db",
                "name": "메인 데이터베이스",
                "status": "active",
                "host": "localhost",
                "port": "5432",
                "dbms": "postgresql",
            },
            {
                "server_type": "db",
                "name": "캐시 데이터베이스",
                "status": "inactive",
                "host": "cache.example.com",
                "port": "3306",
                "dbms": "mysql",
            },
        ]
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
            self._remove_server(server_data)
        return handler
    
    def _remove_server(self, server_data):
        """서버 제거"""
        self.servers = [s for s in self.servers if s != server_data]
        self._update_server_list()
    
    def _update_server_list(self):
        """서버 리스트 UI 업데이트"""
        self.server_list_container.controls.clear()
        
        if not self.servers:
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
            for server_data in self.servers:
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
                )
                self.server_list_container.controls.append(item.build())
        
        # 페이지에 추가된 경우에만 update 호출
        try:
            self.server_list_container.update()
        except RuntimeError:
            # 아직 페이지에 추가되지 않은 경우 무시
            pass
    
    def add_server(self, server_data: dict):
        """새 서버 추가"""
        self.servers.append(server_data)
        self._update_server_list()
    
    def build(self) -> ft.Column:
        """뷰 빌드"""
        # 초기 데이터 로드
        if not self.servers:
            self._load_sample_data()
        
        return ft.Column([
            main_pannel_title("서버 목록보기"),
            ft.Divider(height=15),
            ft.Text("등록된 서버 목록을 확인할 수 있습니다.", size=14, color="#718096"),
            ft.Container(height=10),
            self.server_list_container,
        ], expand=True, align=ft.Alignment(0, -1), scroll=ft.ScrollMode.AUTO)


# 뷰 인스턴스 생성
_server_list_view_instance = ServerListView()
server_list_view = _server_list_view_instance.build()