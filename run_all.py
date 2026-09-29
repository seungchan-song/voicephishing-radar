# [P1] 전체 과정을 순서대로 한 번 실행한다
#   python run_all.py
# 수집 -> 분류 -> 분석 -> 형식 검사 -> 그래프 (notify=True면 메일, Notion까지)
# scheduler.py도 이 run()을 부른다.
import subprocess
import sys
from check_result import check
from common import load_result

STEPS = ["collect_public.py", "collect_news.py", "classify.py", "analysis.py"]
NOTIFY_STEPS = ["mailer.py", "notion_sync.py"]


def run_file(filename):
    print("실행:", filename)
    subprocess.run([sys.executable, filename], check=True)  # 지금 쓰는 파이썬으로 실행, 오류가 나면 멈춘다


def run(notify=False):
    for filename in STEPS:
        run_file(filename)

    errors = check(load_result())
    if errors:
        print("result.json 형식 오류:", errors)
        return

    run_file("charts.py")
    if notify:
        for filename in NOTIFY_STEPS:
            run_file(filename)


if __name__ == "__main__":
    run()
