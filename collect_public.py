# [B1] 경찰청 CSV 3개 -> MongoDB stats 컬렉션 + data/processed/stats.json
#   python collect_public.py
#
# 저장할 문서 모양 (노션 "데이터 형식 약속 -> stats")
#   {"type": "age", "year": 2025, "group": "60대", "count": 5801, "amount": None}
#   {"type": "region", "year": 2025, "group": "서울", "count": 6029, "amount": 402800000000}
# - 연령별은 amount가 항상 None
# - 지역별 amount는 원 단위(억원 x EOK), 2023~2025만 있고 나머지는 None
# - 전부 240개 (연령 6개 x 10년 + 지역 18곳 x 10년)
# [B1] 경찰청 CSV 3개 -> MongoDB stats 컬렉션 + data/processed/stats.json
#   python collect_public.py
import json
import pandas as pd
from config import AGE_CSV, EOK, REGION_AMOUNT_CSV, REGION_COUNT_CSV, STATS_JSON
from db import create_indexes, get_db


def get_all_docs():
    # 1) 연령별: 연도가 행, 연령대가 열 → "연도·연령대·건수" 한 줄씩으로 펼치기
    age = pd.read_csv(AGE_CSV, encoding="cp949")
    age = age.melt(id_vars="구분", var_name="group", value_name="count").rename(
        columns={"구분": "year"}
    )
    # "2025년" -> 2025 변환 (안전한 정수 변환)
    age["year"] = age["year"].astype(str).str.replace("년", "").astype(int)
    age["type"] = "age"
    age["amount"] = None  # 연령별 CSV에는 금액이 없음

    # 2) 지역별: 건수 CSV와 금액 CSV를 각각 펼친 뒤 (시도청, 연도) 기준으로 합치기
    cnt = pd.read_csv(REGION_COUNT_CSV, encoding="cp949").melt(
        id_vars="시도청", var_name="year", value_name="count"
    )
    amt = pd.read_csv(REGION_AMOUNT_CSV, encoding="cp949").melt(
        id_vars="시도청", var_name="year", value_name="amount"
    )
    region = cnt.merge(amt, on=["시도청", "year"], how="left").rename(
        columns={"시도청": "group"}
    )
    region["year"] = (
        region["year"].astype(str).str.replace("년", "").astype(int)
    )  # "2025년" → 2025
    region["type"] = "region"

    # 3) 하나로 합쳐서 문서 목록으로 만들기
    docs = pd.concat([age, region])[
        ["type", "year", "group", "count", "amount"]
    ].to_dict("records")
    for d in docs:  # 금액: 억원 → 원, 없으면 None
        d["amount"] = (
            None if pd.isna(d["amount"]) else int(d["amount"]) * 100_000_000
        )

    return docs


def save(docs):
    db = get_db()
    create_indexes()
    db.stats.delete_many({})  # 기존 데이터 초기화

    # MongoDB 저장 (insert_many 사용)
    if docs:
        # insert_many 실행 시 원본 dict에 _id가 붙는 것을 방지하기 위해 dict 복사본 전달
        db.stats.insert_many([dict(d) for d in docs])

    # stats.json 파일 저장
    with open(STATS_JSON, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 문서 목록 생성
    docs = get_all_docs()

    # DB 및 JSON 파일 저장 실행
    save(docs)

    # 데이터 개수 확인
    age_count = sum(1 for d in docs if d["type"] == "age")
    region_count = sum(1 for d in docs if d["type"] == "region")

    print("age 개수:", age_count)  # 60
    print("region 개수:", region_count)  # 180
    print("전체 개수:", len(docs), "개 (240개면 정상)")
    print("-" * 40)

    # 2025년 데이터 합계 검증
    age_sum_2025 = sum(
        d["count"] for d in docs if d["type"] == "age" and d["year"] == 2025
    )
    region_sum_2025 = sum(
        d["count"] for d in docs if d["type"] == "region" and d["year"] == 2025
    )

    print(f"2025년 연령별 건수 합계: {age_sum_2025:,}건")
    print(f"2025년 지역별 건수 합계: {region_sum_2025:,}건")

    if age_sum_2025 == 23360 and region_sum_2025 == 23360:
        print("✅ 검증 성공: 둘 다 23,360건으로 일치합니다!")
    else:
        print("❌ 검증 실패: 값을 확인해 보세요.")