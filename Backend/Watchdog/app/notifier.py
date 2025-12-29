try:
    from .base import Notifier, Message
except:
    from base import Notifier, Message


class EmailNotifier(Notifier):
    def send(self, msg: Message) -> None:
        print(f"sending email...\ntitle: {msg.title}\n{msg.body}\n")


class SlackNotifier(Notifier):
    def send(self, msg: Message):
        print(f"sending slack alert...\n{msg.body}\n")