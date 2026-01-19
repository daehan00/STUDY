import flet as ft
from app.state.app_state import AppState
from app.services.server_service import ServerService
from app.services.monitor_service import MonitorService
from app.utils.server_logger import LogManager
from app.gui.components.pannels.main_panel import MainPanel
from app.gui.components.bars.sidebar import Sidebar
from app.gui.components.bars.menubar import create_menubar
from app.config.user_config import user_setting

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1000
    page.window.height = 600
    page.padding = 0
    
    # 타이틀 바 숨기기 (OS 기본 타이틀 바 제거)
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = False

    # 1. 상태 및 서비스 초기화
    app_state = AppState()
    server_service = ServerService()
    
    # 초기 데이터 로드
    initial_servers = {
        s['id']: s for s in server_service.get_all_servers()
    }
    app_state.set_servers(initial_servers)
    
    # ServerService 변경사항을 AppState에 동기화
    def sync_server_change(event_type, data):
        if event_type == "add":
            app_state.add_server(data)
        elif event_type == "update":
            app_state.update_server(data['id'], data)
        elif event_type == "delete":
            app_state.remove_server(data['id'])
    
    server_service.add_listener(sync_server_change)
    
    # MonitorService 초기화 (AppState 의존성 제거)
    monitor_service = MonitorService()
    
    # MonitorService 상태 변경 리스너 -> AppState 업데이트 연결
    def sync_monitor_status(server_id, status):
        app_state.update_server(server_id, {'status': status})
    
    monitor_service.add_listener(sync_monitor_status)

    max_log = user_setting.get("max_logs")
    if not isinstance(max_log, int):
        max_log = 100
    
    log_manager = LogManager(max_log)
    # LogManager -> AppState 로그 동기화 연결
    log_manager.add_listener(app_state.add_log)

    # 기존 로그 AppState에 로드
    for log in log_manager.log:
        app_state.add_log(log)
    
    # 컴포넌트 생성 (AppState 주입)
    main_panel = MainPanel(page, app_state)
    
    # 사이드바 메뉴 클릭 핸들러
    def handle_menu_click(view_name: str):
        main_panel.update_content(view_name)
    
    def handel_title_click(_):
        main_panel.update_content("home")
    
    sidebar = Sidebar(page, on_menu_click=handle_menu_click)
    
    # 메뉴바 생성
    menubar = create_menubar(page, handel_title_click)
    
    # 드래그 핸들 (사이드바 크기 조절용)
    def on_pan_update(e: ft.DragUpdateEvent):
        new_width = sidebar.width + int(e.local_delta.x) # type: ignore
        
        sidebar.update_width(new_width)
    
    resize_handle = ft.GestureDetector(
        content=ft.Container(
            width=4,
            bgcolor="#e0e0e0",
        ),
        on_pan_update=on_pan_update,
        drag_interval=2,
        mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
    )

    # 메인 레이아웃
    main_content = ft.Row([
        sidebar.build(),
        resize_handle,
        ft.Container(
            content=main_panel.build(),
            expand=True
        )
    ], spacing=0, expand=True)

    page.add(
        ft.Column([
            menubar,
            ft.Divider(height=1),
            main_content
        ], spacing=0, expand=True)
    )

if __name__ == "__main__":
    ft.run(main)