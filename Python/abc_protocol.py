from typing import Protocol
from abc import ABC, abstractmethod

class Notifier(Protocol):
    def send(self, message: str) -> bool:
        ...
    

class BaseEmail(ABC):
    def connect(self) -> None:
        print("연결됨")
    
    def disconnect(self) -> None:
        print("해제됨")

    @abstractmethod
    def send(self, message: str) -> bool:
        ...


class Gmail(BaseEmail):
    def send(self, message: str) -> bool:
        print("Gmail 전송:", message)
        return True


class Slack:
    def send(self, message: str) -> bool:
        print("Slack 전송:", message)
        return True


def broadcast(notifiers: list[Notifier], msg: str) -> list[bool]:
    return [noti.send(msg) for noti in notifiers]

notifiers = [Gmail(), Slack()]
broadcast(notifiers, "서버 점검 공지입니다.")


class NotifierFactory:
    _registry = {}

    @classmethod
    def register(cls, lib_class, adapter_class):
        cls._registry[lib_class] = adapter_class
    
    @classmethod
    def register_(cls, lib_class):
        print(f"registering {lib_class.__name__} class...")

        if cls._registry.get(lib_class):
            raise RuntimeError("이미 등록된 클래스입니다!!!")
        
        def wrapper(adapter_class):

            cls._registry[lib_class] = adapter_class
            return adapter_class
        return wrapper

    @classmethod
    def get_notifier(cls, lib_instance) -> Notifier:
        lib_class = type(lib_instance)
        adapter_class = cls._registry.get(lib_class)
        
        if not adapter_class:
            return lib_instance

        return adapter_class(lib_instance)


# 외부 라이브러리이고, 수정 불가능하다고 가정
class KakaoTalk:
    def send_msg(self, msg: str) -> str:
        print("카톡 메시지 전송:", msg)
        return msg

@NotifierFactory.register_(KakaoTalk)
class KakaoAdopter:
    def __init__(self, kakao: KakaoTalk):
        self.lib = kakao
    
    def send(self, message: str) -> bool:
        msg = self.lib.send_msg(message)
        return bool(msg)

# @NotifierFactory.register_(KakaoTalk)
# class KakaoAdopter2:
#     def __init__(self, kakao: KakaoTalk):
#         self.lib = kakao
    
#     def send(self, message: str) -> bool:
#         msg = self.lib.send_msg(message)
#         return bool(msg)

# noti_factory = NotifierFactory()
# noti_factory.register(KakaoTalk, KakaoAdopter)

instances = [Gmail(), Slack(), KakaoTalk()]
notifiers = [NotifierFactory.get_notifier(inst) for inst in instances]

broadcast(notifiers, "공지입니다!")
