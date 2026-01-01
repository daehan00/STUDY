import flet as ft

hint_style=ft.TextStyle(
    weight=ft.FontWeight.W_100,
    italic=True,
    color=ft.Colors.BLUE_GREY,
)

def main_pannel_title(text: str) -> ft.Text:
    return ft.Text(text, size=20, weight=ft.FontWeight.BOLD, color="#2d3748")

