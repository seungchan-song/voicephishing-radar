# [B3] 정해진 시간마다 전체 과정(run_all.py)을 자동 실행한다
#   python scheduler.py
#
# 시연할 때는 DEMO = True (1분마다), 실제로는 False (매주 월요일 09:00)
import time
from datetime import datetime

import schedule
from run_all import run

DEMO = True

def job():
    # run(notify=True)를 실행한다. 오류가 나도 스케줄러가 멈추지 않게 try/except로 감싼다
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] 전체 프로세스(run_all) 자동 실행 시작...")
    
    try:
        run(notify=True)
        print(f"[{now_str}] 전체 프로세스 실행 완료!")
    except Exception as e:
        print(f"[{now_str}] ❌ 실행 중 오류 발생 (스케줄러는 계속 유지됨): {e}")

# DEMO면 schedule.every(1).minutes.do(job), 아니면 schedule.every().monday.at("09:00").do(job)
if DEMO:
    schedule.every(1).minutes.do(job)
    print("[시연 모드] 1분 간격으로 스케줄러가 동작합니다.")
else:
    schedule.every().monday.at("09:00").do(job)
    print("[운영 모드] 매주 월요일 09:00에 스케줄러가 동작합니다.")

if __name__ == "__main__":
    print("스케줄러 가동 중... (종료하려면 Ctrl + C)")
    while True:
        schedule.run_pending()
        time.sleep(1)