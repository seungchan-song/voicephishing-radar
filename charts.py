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
    # 연령대별 피해 건수 막대그래프
    data = result["by_age"]

    groups = [item["group"] for item in data]
    counts = [item["count"] for item in data]

    plt.figure(figsize=(8, 5))
    plt.bar(groups, counts)

    plt.title("연령대별 피해 건수")
    plt.xlabel("연령대")
    plt.ylabel("피해 건수")

    plt.tight_layout()
    plt.savefig(CHART_AGE)
    plt.close()


def chart_region(result):
    # 시도청별 피해금액 가로 막대그래프
    data = result["by_region"]

    regions = [item["group"] for item in data]
    amounts = [item["amount"] / 100000000 for item in data]

    plt.figure(figsize=(10, 8))
    plt.barh(regions, amounts)
    plt.gca().invert_yaxis()  # 금액이 큰 지역이 맨 위에 오도록

    plt.title("지역별 피해 금액")
    plt.xlabel("피해 금액 (억 원)")
    plt.ylabel("지역")

    plt.tight_layout()
    plt.savefig(CHART_REGION)
    plt.close()


def chart_methods(result):
    # 수법별 기사 수 막대그래프
    data = result["method_counts"]

    methods = list(data.keys())
    counts = list(data.values())

    plt.figure(figsize=(9, 5))
    plt.bar(methods, counts)

    plt.title("수법별 기사 수")
    plt.xlabel("수법")
    plt.ylabel("기사 수")

    plt.xticks(rotation=30)

    plt.tight_layout()
    plt.savefig(CHART_METHODS)
    plt.close()


def chart_yearly(result):
    # 연도별 피해 건수 선그래프
    data = result["yearly"]

    years = [item["year"] for item in data]
    counts = [item["count"] for item in data]

    plt.figure(figsize=(9, 5))
    plt.plot(years, counts, marker="o")

    plt.title("연도별 피해 건수")
    plt.xlabel("연도")
    plt.ylabel("피해 건수")

    plt.xticks(years)

    plt.tight_layout()
    plt.savefig(CHART_YEARLY)
    plt.close()


if __name__ == "__main__":
    result = load_result()

    chart_age(result)
    chart_region(result)
    chart_methods(result)
    chart_yearly(result)

    print("그래프 저장 완료")