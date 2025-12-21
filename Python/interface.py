from abc import ABCMeta, abstractmethod
from typing import Union

class Payment(metaclass=ABCMeta):    
    def pay(self, amount: Union[str, int]):
        try:
            target_amount = int(amount)
            self._process_payment(target_amount)
        except ValueError:
            print("결제 실패: 유효하지 않은 금액 단위입니다.")

    @abstractmethod
    def _process_payment(self, amount: int):
        ...

class KakaoPay(Payment):
    def _process_payment(self, amount: int):
        print(f"카카오페이로 {amount}원이 결제되었습니다.")

class NaverPay(Payment):
    def navpay(self, abc: str):
        print(f"네이버페이로 {abc}원이 결제되었습니다.")

class TossPay(Payment):
    def _process_payment(self, amount: int):
        print(f"토스페이로 {amount}원이` 결제되었습니다.")

pay = KakaoPay()
pay.pay(200)

# interesting point
toss_pay = TossPay()
toss_pay.pay("200")

# error case
nav_pay = NaverPay()
nav_pay.navpay("123")
