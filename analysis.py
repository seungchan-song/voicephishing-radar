# MongoDB stats, news -> data/processed/result.json
#   python analysis.py
#   python check_result.py   <- 형식 검사
#
# result.json 모양은 노션 "가짜 result.json"과 똑같아야 한다.
# B1: latest_year, analyze_age, analyze_region, analyze_yearly
# P2: analyze_news (완성) 
# P1: make_result (완성)
import os
from datetime import datetime, timedelta
from common import load_result, save_result
from config import RESULT_JSON, TAGS
from db import get_db


def latest_year():
    # TODO(B1): 금액이 있는 region 문서 중 가장 최근 연도를 돌려준다 (지금은 2025)
    pass


def analyze_age(year):
    # TODO(B1): [{"group": "20대이하", "count": 5770, "ratio": 24.7}, ...] 6개를 돌려준다
    # 순서는 config.AGE_GROUPS와 같게, ratio는 전체 대비 %(소수 첫째 자리)
    pass


def analyze_region(year):
    # TODO(B1): [{"group", "count", "amount", "amount_per_case", "ratio"}, ...] 18개를 돌려준다
    # amount가 큰 순서로 정렬, amount_per_case = amount // count
    pass


def analyze_yearly():
    # TODO(B1): [{"year": 2016, "count": ..., "amount": None}, ...] 연도별 전국 합계를 돌려준다
    # region 문서 기준. 그해 금액이 없으면 amount는 None
    pass

def analyze_news():
    # TODO(P2): total_news, period, top_methods, method_counts 4개를 돌려준다
    # period = {"start": 가장 오래된 date, "end": 가장 최근 date}
    # method_counts = 분석 대상 태그별 기사 수
    # top_methods = "기타", "무관"을 뺀 상위 3개,
    #               각각 가장 최근 기사 1개를 sample로

    db = get_db()

    # MongoDB 뉴스 중 '무관'으로 분류된 기사는 분석에서 제외
    relevant_articles = []

    for article in db.news.find():
        tags = article.get("tags", [])

        if "무관" not in tags:
            relevant_articles.append(article)

    # 가장 최근 기사 날짜를 기준으로 최근 30일만 분석
    articles = []

    if relevant_articles:
        newest_date = max(
            datetime.strptime(article["date"], "%Y-%m-%d")
            for article in relevant_articles
        )

        start_date = newest_date - timedelta(days=30)

        for article in relevant_articles:
            article_date = datetime.strptime(
                article["date"],
                "%Y-%m-%d"
            )

            if start_date <= article_date <= newest_date:
                articles.append(article)

    total_news = len(articles)

    # 실제 분석 대상 기사의 날짜 범위
    dates = [
        article["date"]
        for article in articles
    ]

    if dates:
        period = {
            "start": min(dates),
            "end": max(dates),
        }
    else:
        period = {
            "start": "",
            "end": "",
        }

    # 무관은 분석 결과에서 제외
    analysis_tags = [
        tag
        for tag in TAGS
        if tag != "무관"
    ]

    # config.TAGS에 아직 무관이 추가되지 않았더라도
    # 기존 6개 태그 기준으로 정상 동작
    method_counts = {}

    for tag in analysis_tags:
        method_counts[tag] = 0

    for article in articles:
        for tag in article.get("tags", []):
            if tag in method_counts:
                method_counts[tag] += 1

    # 기타를 제외한 실제 수법 중 기사 수가 많은 순서
    methods = []

    for tag in analysis_tags:
        if (
            tag != "기타"
            and method_counts[tag] > 0
        ):
            methods.append({
                "name": tag,
                "count": method_counts[tag],
            })

    methods.sort(
        key=lambda x: x["count"],
        reverse=True
    )

    # 상위 3개 수법과 가장 최근 기사
    top_methods = []

    for rank, method in enumerate(
        methods[:3],
        start=1
    ):
        tag = method["name"]

        tagged_articles = []

        for article in articles:
            if tag in article.get("tags", []):
                tagged_articles.append(article)

        sample_article = None

        if tagged_articles:
            sample_article = max(
                tagged_articles,
                key=lambda x: x["date"]
            )

        sample = {
            "title": "",
            "link": "",
            "date": "",
        }

        if sample_article is not None:
            sample = {
                "title": sample_article.get("title", ""),
                "link": sample_article.get("link", ""),
                "date": sample_article.get("date", ""),
            }

        ratio = 0.0

        if total_news > 0:
            ratio = round(
                method["count"] / total_news * 100,
                1
            )

        top_methods.append({
            "rank": rank,
            "name": tag,
            "count": method["count"],
            "ratio": ratio,
            "sample": sample,
        })

    return total_news, period, top_methods, method_counts

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
