# [B1] 경찰청 CSV 3개 -> MongoDB stats 컬렉션 + data/processed/stats.json
#   python collect_public.py
#
# 저장할 문서 모양 (노션 "데이터 형식 약속 -> stats")
#   {"type": "age", "year": 2025, "group": "60대", "count": 5801, "amount": None}
#   {"type": "region", "year": 2025, "group": "서울", "count": 6029, "amount": 402800000000}
# - 연령별은 amount가 항상 None
# - 지역별 amount는 원 단위(억원 x EOK), 2023~2025만 있고 나머지는 None
# - 전부 240개 (연령 6개 x 10년 + 지역 18곳 x 10년)
# 노션 5-① 에 실제 CSV로 테스트한 예시 코드가 있으니 참고한다.
import json
import pandas as pd
from config import AGE_CSV, REGION_COUNT_CSV, REGION_AMOUNT_CSV, STATS_JSON, EOK
from db import get_db, create_indexes


def load_age():
    # TODO(B1): 연령별 CSV를 읽어서 type이 "age"인 문서 60개의 리스트를 돌려준다
    # 힌트: pd.read_csv(AGE_CSV, encoding="cp949") -> melt
    pass


def load_region():
    # TODO(B1): 지역별 건수 CSV와 금액 CSV를 합쳐서 type이 "region"인 문서 180개의 리스트를 돌려준다
    # 힌트: 두 CSV를 각각 melt -> merge -> "2025년"을 2025로 -> 금액 x EOK
    pass


def save(docs):
    db = get_db()
    create_indexes()
    db.stats.delete_many({})  # 여러 번 실행해도 중복되지 않게 기존 데이터를 지운다
    for doc in docs:
        db.stats.insert_one(dict(doc))  # dict(doc): 원본에 _id가 붙지 않게 복사해서 넣는다

    with open(STATS_JSON, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    docs = load_age() + load_region()
    save(docs)
    print("stats 저장 완료:", len(docs), "개 (240개면 정상)")
