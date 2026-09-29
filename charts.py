# [B2] result.json -> matplotlib 그래프 PNG (static/charts/)
#   python charts.py
#
# 처음에는 가짜 result.json으로 작업한다.
# 파일 이름은 config의 CHART_AGE, CHART_REGION, CHART_METHODS, CHART_YEARLY를 쓴다.
import os
import matplotlib.pyplot as plt
from common import load_result
from config import CHART_AGE, CHART_REGION, CHART_METHODS, CHART_YEARLY

plt.rc("font", family="Malgun Gothic")  # 한글 깨짐 방지 (Windows)
os.makedirs("static/charts", exist_ok=True)


def chart_age(result):
    # TODO(B2): 그래프 1 - 연령대별 피해 건수 막대그래프 (result["by_age"]) -> CHART_AGE로 저장
    pass


def chart_region(result):
    # TODO(B2): 그래프 2 - 시도청별 피해금액 가로 막대그래프 (result["by_region"]) -> CHART_REGION
    # 금액은 원 단위라서 억 원으로 나눠서 그리면 보기 좋다
    pass


def chart_methods(result):
    # TODO(B2): 그래프 3 - 수법별 기사 수 막대그래프 (result["method_counts"]) -> CHART_METHODS
    pass


def chart_yearly(result):
    # TODO(B2, 선택): 그래프 4 - 연도별 피해 건수 선그래프 (result["yearly"]) -> CHART_YEARLY
    pass


if __name__ == "__main__":
    result = load_result()
    chart_age(result)
    chart_region(result)
    chart_methods(result)
    print("그래프 저장 완료")
