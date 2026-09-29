# [P2] news 기사마다 수법 태그(tags)를 붙인다
#   python classify.py
#
# tags에는 config.TAGS 6개만 쓴다: 기관사칭, 가족·지인사칭, 대출빙자, 스미싱, 메신저피싱, 기타
# 키워드가 하나도 없으면 ["기타"]. 키워드는 회의에서 확정한 표(노션 5-③)를 따른다.
from db import get_db

KEYWORDS = {
    "기관사칭": ["검찰", "금감원", "수사관", "경찰", "계좌 동결"],
    "가족·지인사칭": ["엄마", "아들", "딸", "액정", "폰 고장"],
    "대출빙자": ["저금리", "대환대출", "정부지원 대출"],
    "스미싱": ["택배", "청첩장", "부고", "과태료", "건강검진"],
    "메신저피싱": ["카톡", "메신저", "상품권", "원격"],
}


def classify(text):
    # TODO(P2): text에 들어 있는 수법 이름 리스트를 돌려준다. 하나도 없으면 ["기타"]
    pass


if __name__ == "__main__":
    db = get_db()
    count = 0
    for article in db.news.find():
        tags = classify(article["title"] + " " + article["body"])
        db.news.update_one({"_id": article["_id"]}, {"$set": {"tags": tags}})
        count += 1
    print("태그 붙임:", count, "건")
