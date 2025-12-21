class Logger:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        print(f"[{self.name}] 기록을 시작합니다.")
        return self
    
    def __exit__(self, type, value, traceback):
        if type:
            print(f"[{self.name}] 에러 발생!")
        
        print(f"[{self.name}] 기록을 종료합니다.")
        return True
    
    def error_method(self):
        int("data")

with Logger("작업 A") as log:
    print(" 작업 실행...")
    log.error_method()
    print("다음 작업 수행")

print("프로그램 종료")
        