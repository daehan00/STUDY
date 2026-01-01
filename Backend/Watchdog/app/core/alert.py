try:
    from .base import BaseWatcher, Notifier,BaseCheckResult
    from .models import Message, Status, MessageGrade
    from .notifier import EmailNotifier, SlackNotifier
except ImportError:
    from base import BaseWatcher, Notifier, BaseCheckResult
    from models import Message, Status, MessageGrade
    from notifier import EmailNotifier, SlackNotifier

def set_notifiers() -> dict[Status, list[Notifier]]:
    return {
        Status.latency: [EmailNotifier()],
        Status.down: [EmailNotifier(), SlackNotifier()],
        Status.normal: [EmailNotifier(), SlackNotifier()]
    }

def set_alert(
    watcher: BaseWatcher,
    check: BaseCheckResult,
    notifiers: dict[Status, list[Notifier]]
) -> tuple[Message | None, list[Notifier]]:
    level = check.status.value - watcher.status.value
    if level == 0:
        return None, []

    # 새로운 상태 업데이트
    watcher.status = check.status

    grade: MessageGrade | None = None

    if level < 0:
        grade = MessageGrade.resolved

    if check.status == Status.down:
        grade = MessageGrade.critical
    
    if check.status == Status.latency:
        grade = MessageGrade.warning

    if not grade:
        raise KeyError(f"[{check.status}] status가 정의되지 않았습니다.")

    message = make_message_text(watcher.template, check, grade)
    
    title = f"[{watcher.sign}] {grade.upper()}"
    
    return (
        Message(grade=grade, title=title, body=message),
        notifiers[check.status]
    )

def make_message_text(template: str, result: BaseCheckResult, grade: str):
    data = result.model_dump(mode='json')
    return f"{grade.upper()} ISSUE: Your Service {result.status.name.upper()}.\n\n{template.format(**data)}"


if __name__ == "__main__":
    class Test:
        def __init__(self) -> None:
            self.status = 0
    
    def test_func(test: Test) -> None:
        test.status = 1
        return
    
    t = Test()
    test_func(t)
    print(t.status)

    def context():
        num = 0
        def counter():
            nonlocal num
            num += 1
            return num
        return counter
        
    c = context()
    print(c())
    print(c())
    print(c())
    print(c())
