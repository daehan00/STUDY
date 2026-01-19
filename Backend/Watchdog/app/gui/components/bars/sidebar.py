import flet as ft

class Sidebar:
    def __init__(self, page: ft.Page, on_menu_click=None):
        self.page = page
        self.width = 183
        self.min_width = 183  # 글자가 아래로 넘어가지 않는 최소 너비
        self.collapsed_width = 60  # 아이콘만 보이는 너비
        self.max_width = 400
        self.is_collapsed = False
        self.on_menu_click = on_menu_click  # 메뉴 클릭 콜백
        
    def build_collapsed(self):
        """아이콘만 있는 축소된 사이드바"""
        return ft.Column([
            # 헤더 영역 (비워둠)
            ft.Container(height=15),
            ft.Divider(height=1),
            
            # 아이콘 메뉴
            ft.Container(
                content=ft.Column([
                    # 서버 관리 아이콘 + 팝업 메뉴
                    ft.PopupMenuButton(
                        icon=ft.Icons.DNS,
                        icon_size=24,
                        icon_color="#4a5568",
                        tooltip="서버 관리",
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=16),
                                    ft.Text("서버 추가하기", size=13),
                                ], spacing=10),
                                on_click=lambda _: self.on_menu_click("add_server") if self.on_menu_click else None
                            ),
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.LIST, size=16),
                                    ft.Text("서버 목록보기", size=13),
                                ], spacing=10),
                                on_click=lambda _: self.on_menu_click("server_list") if self.on_menu_click else None
                            ),
                        ],
                    ),
                    ft.Divider(height=1),
                    # 알림 관리 아이콘 + 팝업 메뉴
                    ft.PopupMenuButton(
                        icon=ft.Icons.NOTIFICATIONS_ACTIVE,
                        icon_size=24,
                        icon_color="#4a5568",
                        tooltip="알림 관리",
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.SETTINGS, size=16),
                                    ft.Text("알림 채널 설정", size=13),
                                ], spacing=10),
                                on_click=lambda _: self.on_menu_click("notification_settings") if self.on_menu_click else None
                            ),
                        ],
                    ),
                    ft.Divider(height=1),
                    ft.PopupMenuButton(
                        icon=ft.Icons.CHECKROOM,
                        icon_size=24,
                        icon_color="#4a5568",
                        tooltip="실행 기록 확인",
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.TERMINAL, size=16),
                                    ft.Text("서버 로그 확인", size=13),
                                ], spacing=10),
                                on_click=lambda _: self.on_menu_click("log_view") if self.on_menu_click else None
                            ),
                        ],
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                expand=True,
                padding=ft.Padding.only(top=10)
            )
        ])
    
    def build_expanded(self):
        """전체 텍스트가 있는 확장된 사이드바"""
        return ft.Column([
            # 헤더
            ft.Container(
                content=ft.Text(
                    "기능 목록",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                padding=15
            ),
            ft.Divider(height=1),
            
            # 기능 목록
            ft.Container(
                content=ft.Column([
                    # 서버 관리
                    ft.ExpansionTile(
                        title=ft.Text("서버 관리", size=15, weight=ft.FontWeight.W_500),
                        # leading=ft.Icon(ft.Icons.DNS, size=20, color="#4a5568"),
                        controls=[
                            ft.ListTile(
                                title=ft.Text("서버 추가하기", size=13),
                                leading=ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=18),
                                dense=True,
                                content_padding=ft.Padding.only(left=30, right=10),
                                on_click=lambda _: self.on_menu_click("add_server") if self.on_menu_click else None
                            ),
                            ft.ListTile(
                                title=ft.Text("서버 목록보기", size=13),
                                leading=ft.Icon(ft.Icons.LIST, size=18),
                                dense=True,
                                content_padding=ft.Padding.only(left=30, right=10),
                                on_click=lambda _: self.on_menu_click("server_list") if self.on_menu_click else None
                            ),
                        ],
                        expand=True,
                        expanded=True
                    ),
                    # 알림 관리
                    ft.ExpansionTile(
                        title=ft.Text("알림 관리", size=15, weight=ft.FontWeight.W_500),
                        # leading=ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=20, color="#4a5568"),
                        controls=[
                            ft.ListTile(
                                title=ft.Text("알림 채널 설정", size=13),
                                leading=ft.Icon(ft.Icons.SETTINGS, size=18),
                                dense=True,
                                content_padding=ft.Padding.only(left=30, right=10),
                                on_click=lambda _: self.on_menu_click("notification_settings") if self.on_menu_click else None
                            ),
                        ],
                        expand=True,
                        expanded=True
                    ),
                    ft.Divider(height=1),
                    ft.ExpansionTile(
                        title=ft.Text("실행 기록 확인", size=15, weight=ft.FontWeight.W_500),
                        # leading=ft.Icon(ft.Icons.CHECKROOM, size=20, color="#4a5568"),
                        controls=[
                            ft.ListTile(
                                title=ft.Text("서버 로그 확인", size=13),
                                leading=ft.Icon(ft.Icons.TERMINAL, size=18),
                                dense=True,
                                content_padding=ft.Padding.only(left=30, right=10),
                                on_click=lambda _: self.on_menu_click("log_view") if self.on_menu_click else None
                            ),
                        ],
                        expand=True,
                        expanded=True
                    ),
                ], scroll=ft.ScrollMode.AUTO, expand=True),
                expand=True
            )
        ], align=ft.Alignment(0,-1), scroll=ft.ScrollMode.AUTO)
        
    def build(self):
        self.is_collapsed = self.width < self.min_width
        
        self.container = ft.Container(
            content=self.build_collapsed() if self.is_collapsed else self.build_expanded(),
            width=self.width,
            bgcolor="#f7fafc",
            padding=5
        )
        return self.container
    
    def update_width(self, new_width):
        self.width = max(self.collapsed_width, min(new_width, self.max_width))
        was_collapsed = self.is_collapsed
        self.is_collapsed = self.width < self.min_width
        
        # 상태가 변경되었을 때만 콘텐츠를 다시 빌드
        if was_collapsed != self.is_collapsed:
            self.container.content = self.build_collapsed() if self.is_collapsed else self.build_expanded()
        
        self.container.width = self.width
        self.page.update()
