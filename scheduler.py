# [B3] 정해진 시간마다 전체 과정(run_all.py)을 자동 실행한다
#   python scheduler.py
#
# 시연할 때는 DEMO = True (1분마다), 실제로는 False (매주 월요일 09:00)
import time
import schedule
from run_all import run

DEMO = True


def job():
    # TODO(B3): run(notify=True)를 실행한다. 오류가 나도 스케줄러가 멈추지 않게 try/except로 감싼다
    pass


# TODO(B3): DEMO면 schedule.every(1).minutes.do(job), 아니면 schedule.every().monday.at("09:00").do(job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
