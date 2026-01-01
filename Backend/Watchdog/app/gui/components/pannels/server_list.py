import flet as ft

from styles.text import main_pannel_title

server_list_view = ft.Column([
    main_pannel_title("서버 목록보기"),
    ft.Divider(height=15),
    ft.Text("등록된 서버 목록을 확인할 수 있습니다.", size=14, color="#718096"),
], expand=True, align=ft.Alignment(0,-1), scroll=ft.ScrollMode.AUTO)