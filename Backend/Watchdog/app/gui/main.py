import flet as ft
from components.pannels.main_panel import MainPanel
from components.bars.sidebar import Sidebar
from components.bars.menubar import drag_area

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1000
    page.window.height = 600
    page.padding = 0
    
    # 타이틀 바 숨기기 (OS 기본 타이틀 바 제거)
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = False

    # 컴포넌트 생성
    main_panel = MainPanel(page)
    
    # 사이드바 메뉴 클릭 핸들러
    def handle_menu_click(view_name: str):
        main_panel.update_content(view_name)
    
    sidebar = Sidebar(page, on_menu_click=handle_menu_click)
    
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
            drag_area,
            ft.Divider(height=1),
            main_content
        ], spacing=0, expand=True)
    )

if __name__ == "__main__":
    ft.run(main)