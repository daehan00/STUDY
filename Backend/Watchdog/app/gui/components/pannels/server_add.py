import flet as ft
import json
from typing import Dict, Tuple
import sys
from pathlib import Path

# 부모 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from styles.text import hint_style, main_pannel_title
from styles.colors import error_red
from services import ServerService
from config import DBMS_PORTS, SERVER_TYPES


class ServerAddView:
    """서버 추가 뷰 클래스"""
    
    def __init__(self):
        self.server_service = ServerService()
        self.radio_container: ft.Container
        self.radio_error_text: ft.Text
        self.dbms_container: ft.Container | None = None
        self.dbms_error_text: ft.Text | None = None
        self.server_type_group: ft.RadioGroup
        self.input_fields: ft.Column
        self.message: ft.Text
        self._initialize_components()
    
    def _initialize_components(self):
        """컴포넌트 초기화"""
        self.server_type_group = ft.RadioGroup(
            content=ft.Column(
                controls=[
                    ft.Radio(value="web", label="WEB"),
                    ft.Radio(value="db", label="DataBase"),
                ]
            ),
            on_change=self._handle_server_type_change
        )
        
        self.radio_container = ft.Container(
            content=self.server_type_group,
            padding=3,
            border_radius=5,
            width=300,
        )

        self.radio_container.border = ft.Border.all(1, ft.Colors.BLACK)
        
        self.radio_error_text = ft.Text("", size=12, color=error_red)
        self.input_fields = ft.Column(controls=[])
        self.message = ft.Text()
    
    def _clear_error(self, e):
        """입력 시 에러 메시지 제거"""
        if e.control.error:
            e.control.error = None
            e.control.update()
    
    def _clear_radio_error(self):
        """라디오 버튼 에러 제거"""
        self.radio_container.border = ft.Border.all(1, ft.Colors.BLACK)
        self.radio_error_text.value = ""
        self.radio_error_text.update()
        self.radio_container.update()
    
    def _clear_dbms_error(self):
        """DBMS 라디오 버튼 에러 제거"""
        if self.dbms_container and self.dbms_error_text:
            self.dbms_container.border = ft.Border.all(1, ft.Colors.BLACK)
            self.dbms_error_text.value = ""
            self.dbms_error_text.update()
            self.dbms_container.update()
    
    def _create_web_fields(self) -> list:
        """웹 서버 입력 필드 생성"""
        return [
            ft.TextField(
                label="NAME *",
                hint_text="메인 웹서버",
                hint_style=hint_style,
                max_length=100,
                on_change=self._clear_error
            ),
            ft.TextField(
                label="URL *",
                hint_text="https://example.com",
                hint_style=hint_style,
                max_length=100,
                input_filter=ft.InputFilter(allow=False, regex_string=r"[0-9a-z]*$"),
                on_change=self._clear_error
            ),
            ft.TextField(
                label="PORT",
                hint_text="443",
                hint_style=hint_style,
                max_length=5,
                input_filter=ft.NumbersOnlyInputFilter(),
                on_change=self._clear_error
            ),
            ft.TextField(
                label="ENDPOINT *",
                hint_text="/api/health",
                hint_style=hint_style,
                max_length=100,
                input_filter=ft.InputFilter(allow=False, regex_string=r"[0-9a-z]*$"),
                on_change=self._clear_error
            ),
            ft.TextField(
                label="LATENCY",
                hint_text="30(초)",
                hint_style=hint_style,
                max_length=3,
                input_filter=ft.NumbersOnlyInputFilter(),
                on_change=self._clear_error
            ),
            ft.TextField(
                label="AUTH_KEY",
                hint_text="x-api-key",
                hint_style=hint_style,
                max_length=100,
                input_filter=ft.InputFilter(allow=False, regex_string=r"[0-9a-z]*$"),
                on_change=self._clear_error
            ),
        ]
    
    def _handle_dbms_change(self, e, port_field: ft.TextField):
        """DBMS 선택 변경 핸들러"""
        self._clear_dbms_error()
        
        dbms = e.control.value
        port_field.value = DBMS_PORTS.get(dbms, "")
        port_field.update()
    
    def _create_db_fields(self) -> list:
        """데이터베이스 서버 입력 필드 생성"""
        port_field = ft.TextField(
            label="PORT *",
            value="5432",
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=5,
            on_change=self._clear_error
        )
        
        dbms_group = ft.RadioGroup(
            content=ft.Column(
                controls=[
                    ft.Radio(value="mysql", label="MySQL"),
                    ft.Radio(value="postgresql", label="PostgreSQL"),
                ]
            ),
            on_change=lambda e: self._handle_dbms_change(e, port_field),
        )
        
        self.dbms_container = ft.Container(
            content=dbms_group,
            padding=3,
            border_radius=5,
            width=300
        )

        self.dbms_container.border = ft.Border.all(1, ft.Colors.BLACK)
        
        self.dbms_error_text = ft.Text("", size=12, color=ft.CupertinoColors.DESTRUCTIVE_RED)
        
        return [
            ft.TextField(
                label="NAME *",
                hint_text="메인 데이터베이스",
                hint_style=hint_style,
                max_length=100,
                on_change=self._clear_error
            ),
            ft.Text("DBMS *", size=14, color="#718096"),
            self.dbms_container,
            self.dbms_error_text,
            ft.TextField(
                label="HOST *",
                hint_text="localhost",
                hint_style=hint_style,
                max_length=100,
                input_filter=ft.InputFilter(allow=False, regex_string=r"[0-9a-z]*$"),
                on_change=self._clear_error
            ),
            port_field,
            ft.TextField(
                label="DB_NAME *",
                hint_text="mydb",
                hint_style=hint_style,
                max_length=100,
                on_change=self._clear_error
            ),
            ft.TextField(
                label="USERNAME *",
                max_length=100,
                on_change=self._clear_error
            ),
            ft.TextField(
                label="PASSWORD *",
                password=True,
                can_reveal_password=True,
                max_length=100,
                on_change=self._clear_error
            ),
        ]
    
    def _handle_server_type_change(self, e):
        """서버 타입 변경 핸들러"""
        self._clear_radio_error()
        
        server_type = self.server_type_group.value
        
        if server_type == "web":
            self.input_fields.controls = self._create_web_fields()
        elif server_type == "db":
            self.input_fields.controls = self._create_db_fields()
        else:
            self.input_fields.controls = []
        
        self.input_fields.update()
    
    def _validate_server_type(self) -> bool:
        """서버 타입 검증"""
        if not self.server_type_group.value:
            self.radio_container.border = ft.Border.all(1, error_red)
            self.radio_error_text.value = "서버 타입을 선택해주세요."
            self.radio_container.update()
            self.radio_error_text.update()
            return False
        return True
    
    def _validate_text_field(self, control: ft.TextField, data: Dict[str, str]) -> bool:
        """텍스트 필드 검증"""
        label = str(control.label or "")
        is_required = label.endswith("*")
        clean_label = label.replace("*", "").strip()
        value = (control.value or "").strip()
        
        if is_required and not value:
            control.error = f"{clean_label}은(는) 필수 입력 항목입니다."
            control.update()
            return False
        
        if value:
            data[clean_label.lower()] = value
        
        return True
    
    def _validate_dbms_radio(self, control: ft.Container, data: Dict[str, str]) -> bool:
        """DBMS 라디오 그룹 검증"""
        if control.content.value: # type: ignore
            data["dbms"] = control.content.value # type: ignore
            return True
        
        control.border = ft.Border.all(1, error_red)
        idx = self.input_fields.controls.index(control)
        
        if idx + 1 < len(self.input_fields.controls):
            next_control = self.input_fields.controls[idx + 1]
            if isinstance(next_control, ft.Text):
                next_control.value = "DBMS를 선택해주세요."
                next_control.color = error_red
                next_control.update()
        
        control.update()
        return False
    
    def _validate_and_collect_data(self) -> Tuple[bool, Dict[str, str]]:
        """필수 필드 검증 및 데이터 수집"""
        data = {}
        is_valid = self._validate_server_type()
        
        for control in self.input_fields.controls:
            if isinstance(control, ft.TextField):
                if not self._validate_text_field(control, data):
                    is_valid = False
            
            elif isinstance(control, ft.Container) and \
                 hasattr(control, 'content') and \
                 isinstance(control.content, ft.RadioGroup):
                if not self._validate_dbms_radio(control, data):
                    is_valid = False
        
        return is_valid, data
    
    def _handle_submit(self, e):
        """제출 버튼 클릭 핸들러"""
        is_valid, data = self._validate_and_collect_data()
        
        if is_valid:
            try:
                # 서버 타입 추가
                server_data = {
                    "server_type": self.server_type_group.value,
                    **data
                }
                
                # ServerService를 통해 서버 추가
                added_server = self.server_service.add_server(server_data)
                
                self.message.value = f"✅ 서버가 성공적으로 추가되었습니다!\n"
                self.message.value += f"서버 ID: {added_server.get('id')}\n"
                self.message.value += f"서버 타입: {added_server.get('server_type')}\n"
                self.message.color = "#10B981"  # 녹색
                
                # 폼 초기화
                self._reset_form()
                
            except Exception as ex:
                self.message.value = f"❌ 서버 추가 실패: {str(ex)}"
                self.message.color = error_red
        else:
            self.message.value = "필수 입력 항목을 모두 입력해주세요."
            self.message.color = error_red
        
        self.message.update()
    
    def _reset_form(self):
        """폼 초기화"""
        # 서버 타입 라디오 초기화
        self.server_type_group.value = None
        self.server_type_group.update()
        
        # 입력 필드 초기화
        self.input_fields.controls.clear()
        self.input_fields.update()
    
    def build(self) -> ft.Column:
        """뷰 빌드"""
        return ft.Column([
            main_pannel_title("서버 추가하기"),
            ft.Divider(),
            ft.Text("서버 타입 *", size=14, color="#718096"),
            self.radio_container,
            self.radio_error_text,
            # ft.Divider(),
            self.input_fields,
            ft.Button(content="Submit", on_click=self._handle_submit),
            self.message,
        ], expand=True, align=ft.Alignment(0, -1), scroll=ft.ScrollMode.AUTO)


# 뷰 인스턴스 생성
_server_add_view_instance = ServerAddView()
server_add_view = _server_add_view_instance.build()
