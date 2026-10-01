# [B4] result.json의 수법 TOP 3 -> Notion 데이터베이스에 한 줄씩 기록
#   python notion_sync.py
#
# .env에 NOTION_TOKEN, NOTION_DATABASE_ID를 넣어야 한다.
# Notion DB 페이지의 "연결"에 우리 integration을 추가해야 글이 써진다.
# Notion DB 열 이름: 수법(제목), 기사 수(숫자), 대표 기사(URL), 날짜(날짜)
from notion_client import Client
from common import load_result
from config import NOTION_TOKEN, NOTION_DATABASE_ID


def add_row(notion, method, date):
    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "수법": {"title": [{"text": {"content": method["name"]}}]},
            "기사 수": {"number": method["count"]},
            "대표 기사": {"url": method["sample"]["link"]},
            "날짜": {"date": {"start": date}},
        },
    )
    print("추가 완료:", method["rank"], method["name"])


if __name__ == "__main__":
    result = load_result()
    notion = Client(auth=NOTION_TOKEN)
    for method in result["top_methods"]:
        add_row(notion, method, result["generated_at"][:10])
    print("Notion 기록 완료")
