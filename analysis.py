# MongoDB stats, news -> data/processed/result.json
#   python analysis.py
#   python check_result.py   <- 형식 검사
#
# result.json 모양은 노션 "데이터 형식 약속"과 똑같아야 한다.
# B1: latest_year, analyze_age, analyze_region, analyze_yearly
# P2: analyze_news
# P1: make_result
from datetime import datetime, timedelta
from common import save_result
from config import AGE_GROUPS, TAGS
from db import get_db


def latest_year():
    # 금액이 있는 region 문서 중 가장 최근 연도를 돌려준다 (없으면 2025)
    db = get_db()
    docs = list(db.stats.find({"type": "region", "amount": {"$ne": None}}))
    if not docs:
        return 2025
    return max(doc["year"] for doc in docs)


def analyze_age(year):
    # [{"group": "20대이하", "count": 5770, "ratio": 24.7}, ...] 6개를 돌려준다
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
    # [{"group", "count", "amount", "amount_per_case", "ratio"}, ...] 18개를 돌려준다
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
    # [{"year": 2016, "count": ..., "amount": None}, ...] 연도별 전국 합계를 돌려준다
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
    # total_news, period, top_methods, method_counts 4개를 돌려준다
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

# 통계(경찰청 2025년) 기반 인사이트: 사람이 해석을 써서 고정한다. **...** 로 감싼 부분은 화면에서 강조된다.
# 숫자는 result.json의 yearly, by_age, by_region으로 확인한 값이다. 통계 연도가 바뀌면 문장도 다시 쓴다.
STATS_INSIGHTS = [
    "2023→2025년 피해 건수는 **24%** 늘었지만 금액은 **약 2.8배**(4,473억→1조 2,578억 원)가 됐습니다. "
    "1건당 피해액이 2,366만→5,384만 원으로 커져, 사기 한 번의 피해가 훨씬 커졌습니다.",
    "2025년 피해자는 **60대(24.8%)**와 **20대 이하(24.7%)**가 각각 약 4분의 1로 가장 많습니다. "
    "고령층뿐 아니라 청년층 대상 예방 홍보도 필요합니다.",
    "**서울과 경기남부**가 2025년 피해 건수의 **46.6%**, 피해 금액의 **50.8%**를 차지합니다. "
    "서울은 1건당 6,681만 원으로 전국 평균(5,384만 원)보다 1.2배 높습니다.",
]


def make_news_insight(top_methods, total_news):
    # 뉴스 기반 인사이트: 기사가 바뀔 때마다 숫자를 새로 계산해서 문장을 만든다
    if total_news == 0 or len(top_methods) < 2:
        return ""  # 기사가 없으면 문장을 만들지 않는다

    first = top_methods[0]
    second = top_methods[1]
    top_count = first["count"] + second["count"]
    percent = round(top_count / total_news * 100, 1)
    return (f"최근 뉴스 {total_news:,}건 중 **{first['name']}({first['count']}건)·{second['name']}({second['count']}건)** "
            f"기사가 **{percent}%**로 가장 많이 보도됐습니다. 보도가 몰린 이 두 수법을 가장 먼저 조심하세요.")


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

    # 인사이트 = 통계 기반 고정 문장 + 뉴스 기반 자동 문장
    insights = list(STATS_INSIGHTS)
    news_insight = make_news_insight(top_methods, total_news)
    if news_insight:
        insights.append(news_insight)

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
