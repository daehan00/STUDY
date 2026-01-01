import flet as ft

top_menu = ft.Container(
    content=ft.Row([
        # # 맨 왼쪽: macOS 스타일 신호등 버튼
        # ft.Container(
        #     content=ft.Row([
        #         close_button,
        #         minimize_button,
        #         maximize_button,
        #     ], spacing=8),
        #     padding=ft.Padding.only(left=15, right=20)
        # ),
        # 왼쪽: 타이틀 영역
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.MONITOR_HEART, color="#ff6b35", size=24),
                ft.Text("Watchdog", size=18, weight=ft.FontWeight.BOLD, color="#2d3748"),
            ], spacing=10),
            padding=ft.Padding.only(right=15, left=80)
        ),
        # 가운데: 검색창
        ft.Container(
            content=ft.TextField(
                hint_text="Search...",
                border=ft.InputBorder.OUTLINE,
                dense=True,
                prefix_icon=ft.Icons.SEARCH,
                width=350,
                height=35,
            ),
            expand=True,
            alignment=ft.alignment.Alignment(0,0)
        ),
        # 오른쪽: 설정 및 알람 버튼
        ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=25),
                    width=40,
                    height=40,
                    border_radius=5,
                    alignment=ft.Alignment(0,0),
                    tooltip="실행",
                    ink=True,
                    on_click=lambda _: print("실행"),
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.SETTINGS, size=20),
                    width=40,
                    height=40,
                    border_radius=5,
                    alignment=ft.Alignment(0,0),
                    tooltip="설정",
                    ink=True,
                    on_click=lambda _: print("설정"),
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.NOTIFICATIONS, size=20),
                    width=40,
                    height=40,
                    border_radius=5,
                    alignment=ft.Alignment(0,0),
                    tooltip="알림",
                    ink=True,
                    on_click=lambda _: print("알림"),
                ),
            ], spacing=5),
            padding=ft.Padding.only(right=15)
        ),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
    bgcolor="#ffffff",
    padding=ft.Padding.only(left=0, right=15, top=0, bottom=0),
    height=50
)

# 드래그 가능 영역 설정
drag_area = ft.WindowDragArea(content=top_menu)