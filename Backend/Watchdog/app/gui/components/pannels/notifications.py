import flet as ft

from app.gui.styles.text import main_pannel_title

notification_settings_view = ft.Column([
    main_pannel_title("알림 채널 설정"),
    ft.Divider(height=15),
    ft.Text("알림을 받을 채널을 설정할 수 있습니다.", size=14, color="#718096"),
], expand=True, align=ft.Alignment(0,-1), scroll=ft.ScrollMode.AUTO)