import flet as ft
from typing import Callable, List

def create_edit_popup(server_data: dict, on_save: Callable, on_cancel: Callable) -> ft.AlertDialog:
    # 공통 필드
    name_field = ft.TextField(label="서버 이름", value=server_data.get("name") or "")
    port_field = ft.TextField(label="포트", value=server_data.get("port") or "")
    
    controls: List[ft.Control] = [name_field]
    
    # 변수 초기화
    url_field = None
    endpoint_field = None
    latency_field = None
    auth_key_field = None
    
    host_field = None
    dbms_field = None
    db_name_field = None
    username_field = None
    password_field = None
    
    if server_data.get("server_type") == "web":
        url_field = ft.TextField(
            label="URL", 
            value=server_data.get("url") or "", 
            read_only=True, 
            disabled=True
        )
        controls.append(url_field)
        controls.append(port_field)
        
        endpoint_field = ft.TextField(label="ENDPOINT", value=server_data.get("endpoint") or "")
        controls.append(endpoint_field)
        
        latency_field = ft.TextField(label="LATENCY", value=server_data.get("latency") or "")
        controls.append(latency_field)
        
        auth_key_field = ft.TextField(label="AUTH_KEY", value=server_data.get("auth_key") or "")
        controls.append(auth_key_field)
        
    elif server_data.get("server_type") == "db":
        dbms_field = ft.TextField(
            label="DBMS",
            value=server_data.get("dbms", "mysql"),
            read_only=True,
            disabled=True
        )
        controls.append(dbms_field)
        
        host_field = ft.TextField(
            label="HOST", 
            value=server_data.get("host") or "", 
            read_only=True, 
            disabled=True
        )
        controls.append(host_field)
        controls.append(port_field)
        
        db_name_field = ft.TextField(label="DB_NAME", value=server_data.get("db_name") or "")
        controls.append(db_name_field)
        
        username_field = ft.TextField(label="USERNAME", value=server_data.get("username") or "")
        controls.append(username_field)
        
        password_field = ft.TextField(
            label="PASSWORD", 
            value=server_data.get("password") or "", 
            password=True, 
            can_reveal_password=True
        )
        controls.append(password_field)

    def handle_save(e):
        updated_data = {
            "name": name_field.value,
            "port": port_field.value,
        }
        
        if server_data.get("server_type") == "web":
            if endpoint_field: updated_data["endpoint"] = endpoint_field.value
            if latency_field: updated_data["latency"] = latency_field.value
            if auth_key_field: updated_data["auth_key"] = auth_key_field.value
            
        elif server_data.get("server_type") == "db":
            if db_name_field: updated_data["db_name"] = db_name_field.value
            if username_field: updated_data["username"] = username_field.value
            if password_field: updated_data["password"] = password_field.value
            
        if on_save:
            on_save(updated_data)

    def handle_cancel(e):
        if on_cancel:
            on_cancel(e)

    return ft.AlertDialog(
        modal=True,
        title=ft.Text("서버 수정"),
        content=ft.Column(
            controls=controls,
            tight=True,
            width=400,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("취소", on_click=handle_cancel),
            ft.TextButton("저장", on_click=handle_save),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
