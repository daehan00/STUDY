from typing import Any
from typing_extensions import Self
from app.utils.server_logger import FileManager
from app.config.settings import SETTING_FILE, DEFAULT_USER_SETTINGS


class UserConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        
        self._initialized = True
        self.filemanager = FileManager(SETTING_FILE)
        self.config: dict = {}
        self.keys = DEFAULT_USER_SETTINGS.keys()
        self._initialize()
    
    def _initialize(self):
        data = self.filemanager.load()
        if not isinstance(data, dict):
            data = DEFAULT_USER_SETTINGS
            self.filemanager.save(data)
        self.config = data
    
    def _validate_key(self, key: str) -> bool:
        if key in self.keys:
            return True
        return False
    
    def _update(self, key: str, value: Any) -> bool:
        if not self._validate_key(key):
            return False
        
        self.config[key] = value
        return True

    def save_config(self) -> str | None:
        try:
            self.filemanager.save(self.config)
        except Exception as e:
            return str(e)
    
    def update(self, key: str, value: Any) -> str | None:
        if not self._update(key, value):
            return f"failed to update configuration. unknown key [{key}]"
        
        return self.save_config()
    
    def update_all(self, settings: dict) -> str | None:
        fail = []
        retrieve = self.config.copy()
        for k, v in settings.items():
            if not self._update(k, v):
                fail.append(k)
        
        if fail:
            self.config = retrieve
            return f"failed to update configuration. unknown key(s): [{','.join(fail)}]"
        
        return self.save_config()
    
    def get_all(self) -> dict:
        return self.config
    
    def get(self, key: str) -> Any:
        return self.config.get(key)

user_setting = UserConfigManager()

