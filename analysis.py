# MongoDB stats, news -> data/processed/result.json
#   python analysis.py
#   python check_result.py   <- 형식 검사
#
# result.json 모양은 노션 "가짜 result.json"과 똑같아야 한다.
# B1: latest_year, analyze_age, analyze_region, analyze_yearly
# P2: analyze_news
# P1: make_result (완성)
import os
from datetime import datetime
from common import load_result, save_result
from config import AGE_GROUPS, RESULT_JSON
from db import get_db


def latest_year():
    # TODO(B1): 금액이 있는 region 문서 중 가장 최근 연도를 돌려준다 (지금은 2025)
    db = get_db()
    docs = list(db.stats.find({"type": "region", "amount": {"$ne": None}}))
    if not docs:
        return 2025
    return max(doc["year"] for doc in docs)


def analyze_age(year):
    # TODO(B1): [{"group": "20대이하", "count": 5770, "ratio": 24.7}, ...] 6개를 돌려준다
    # 순서는 config.AGE_GROUPS와 같게, ratio는 전체 대비 %(소수 첫째 자리)
    db = get_db()
    docs = list(db.stats.find({"type": "age", "year": year}))

    # 연령대별 건수 맵 생성
    age_map = {doc["group"]: doc["count"] for doc in docs}
    total_count = sum(age_map.values())

    results = []
    for group in AGE_GROUPS:
        count = age_map.get(group, 0)
        ratio = (
            round((count / total_count * 100), 1) if total_count > 0 else 0.0
        )
        results.append({"group": group, "count": count, "ratio": ratio})

    return results


def analyze_region(year):
    # TODO(B1): [{"group", "count", "amount", "amount_per_case", "ratio"}, ...] 18개를 돌려준다
    # amount가 큰 순서로 정렬, amount_per_case = amount // count
    db = get_db()
    docs = list(db.stats.find({"type": "region", "year": year}))

    total_count = sum(doc["count"] for doc in docs)

    results = []
    for doc in docs:
        count = doc["count"]
        amount = doc["amount"] if doc.get("amount") is not None else 0
        amount_per_case = (amount // count) if count > 0 else 0
        ratio = (
            round((count / total_count * 100), 1) if total_count > 0 else 0.0
        )

        results.append(
            {
                "group": doc["group"],
                "count": count,
                "amount": amount,
                "amount_per_case": amount_per_case,
                "ratio": ratio,
            }
        )

    # 피해 금액(amount) 내림차순 정렬
    results.sort(key=lambda x: x["amount"], reverse=True)
    return results


def analyze_yearly():
    # TODO(B1): [{"year": 2016, "count": ..., "amount": None}, ...] 연도별 전국 합계를 돌려준다
    # region 문서 기준. 그해 금액이 없으면 amount는 None
    db = get_db()
    docs = list(db.stats.find({"type": "region"}))

    yearly_data = {}
    for doc in docs:
        y = doc["year"]
        if y not in yearly_data:
            yearly_data[y] = {"count": 0, "amounts": []}

        yearly_data[y]["count"] += doc["count"]
        if doc.get("amount") is not None:
            yearly_data[y]["amounts"].append(doc["amount"])

    results = []
    for y in sorted(yearly_data.keys()):
        c = yearly_data[y]["count"]
        amounts = yearly_data[y]["amounts"]
        a = sum(amounts) if len(amounts) > 0 else None

        results.append({"year": y, "count": c, "amount": a})

    return results


def analyze_news():
    # TODO(P2): total_news, period, top_methods, method_counts 4개를 돌려준다
    # period = {"start": 가장 오래된 date, "end": 가장 최근 date}
    # method_counts = 태그 6개 모두의 기사 수 (0건도 넣기)
    # top_methods = "기타"를 뺀 상위 3개, 각각 가장 최근 기사 1개를 sample로
    pass


def make_result():
    year = latest_year()
    by_age = analyze_age(year)
    by_region = analyze_region(year)
    total_news, period, top_methods, method_counts = analyze_news()

    total_count = 0
    for row in by_age:
        total_count += row["count"]
    total_amount = 0
    for row in by_region:
        total_amount += row["amount"]

    # 사람이 직접 쓰는 insights는 지우지 않고 이어받는다
    insights = []
    if os.path.exists(RESULT_JSON):
        insights = load_result()["insights"]

    return {
        "is_fake": False,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stats_year": year,
        "summary": {"total_count": total_count, "total_amount": total_amount, "total_news": total_news},
        "period": period,
        "by_age": by_age,
        "by_region": by_region,
        "yearly": analyze_yearly(),
        "top_methods": top_methods,
        "method_counts": method_counts,
        "insights": insights,
    }


if __name__ == "__main__":
    save_result(make_result())
    print("result.json 저장 완료")
